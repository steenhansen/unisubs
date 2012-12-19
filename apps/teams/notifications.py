# Amara, universalsubtitles.org
#
# Copyright (C) 2012 Participatory Culture Foundation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.

from httplib2 import Http
from urllib import urlencode

from django.utils.translation import ugettext_lazy as _

from utils import send_templated_email
from utils.metrics import Meter
from unilangs import LanguageCode
from videos.models import Video

import logging
logger = logging.getLogger("team-notifier")

class BaseNotification(object):
    """
    Holds the data needed to prepare a notification.
    Subclasses should be able to translate video_ids
    and language codes with from_internal_lang and
    from_internal_video_id

    Also, subclasses should implement a more specialized version of
    'send_http_request'
    'send_email'
    """
    codec = "unisubs"
    api_name = "partners"
    def from_internal_lang(self, lang_code):
        # we allow empty language codes
        if not lang_code:
            return ""
        return LanguageCode(lang_code, "unisubs").encode(self.codec)

    def to_internal_lang(self, lang_code):
        """
        """
        if not lang_code:
            return ""
        return LanguageCode(lang_code, self.codec).encode("unisubs")


    def to_internal_video_id(self, api_pk):
        """
        Coverts the public api id to the internal video_id for
        this api resource.

        Subclasses mapping to other system's id e.g ted should be able
        to gather the video from this public id
        """
        return Video.objects.get(video_id=api_pk).video_id
        
    def from_internal_video_id(self, video_id, video=None):
        """
        Coverts the internal video id representation (the actual )
        Video.video_id into a public video id. Partners can override
        the logic to fetch to their ids here.
        If a video has already been fetched from the db, it can be passed
        to avoid an extra lookup.
        """
        return video_id if video_id else video.video_id


    def __init__(self, team, partner, event_name,  **kwargs):
        """
        If the event is about new / edits to videos, then language_pk
        will be None else it can be about languages or subtitles.
        """
        from videos.models import Video
        self.team = team
        self.partner = partner
        video_id  = kwargs.pop('video_id', None)
        if video_id:
            self.video = Video.objects.get(video_id=video_id)
        else:
            self.video = None
        self.language_pk = kwargs.pop('language_pk', None)
        self.application_pk = kwargs.pop('application_pk', None)
        self.version_pk = kwargs.pop('version_pk', None)
        if self.language_pk:
            self.language = self.video.subtitlelanguage_set.get(pk=self.language_pk)
            if self.version_pk:
                self.version = self.language.subtitleversion_set.get(pk=self.version_pk)
        else:
            self.language = None
        self.event_name = event_name
        self.api_url = self.get_api_url()

    def get_api_url(self):
        """
        Returns what api url the recipient of this notification should
        query for the latest data. This is team dependent if the team
        has a custom base url.
        """
        from apiv2.api import (
            VideoLanguageResource, VideoResource, ApplicationResource
        )
        from teams.models import Application
        if self.video:
            video_klass = getattr(self.__class__, "video_resource_class", VideoResource)
            if self.language:
                lang_klass = getattr(self.__class__, "language_resource_class", VideoLanguageResource)
                url =  lang_klass(self.api_name).get_resource_uri(self.language)
                if self.version_pk:
                   url += "subtitles/?version_no=%s"  % self.version.version_no
                return url
            else:
                return video_klass(self.api_name).get_resource_uri(self.video)
        elif self.application_pk:
            return ApplicationResource("partners").get_resource_uri(Application.objects.get(pk=self.application_pk))

    @property
    def video_id(self):
        if self.video:
            return self.from_internal_video_id(None, video=self.video)

    @property
    def language_code(self):
        if self.language:
            return  self.from_internal_lang(self.language.language)

    def send_http_request(self, url, basic_auth_username, basic_auth_password):
        h = Http()
        if basic_auth_username and basic_auth_password:
            h.add_credentials(basic_auth_username, basic_auth_password)
            
        project = self.video.get_team_video().project.slug if self.video else None
        data = {
            'event': self.event_name,
            'api_url': self.api_url,
        }
        if self.team:
            data['team'] = self.team.slug
        if self.partner:
            data['partner'] = self.partner.slug
        if project:
            data['project'] = project
        if self.video:
            data['video_id'] = self.video_id
        if self.application_pk:
            data['application_id'] = self.application_pk
        if self.language_code:
            data.update({"language_code":self.language_code} )
        data_sent = data
        data = urlencode(data)
        url = "%s?%s"  % (url , data)
        try:
            resp, content = h.request(url, method="POST", body=data)
            success =  200<= resp.status <400
            if success is False:
                logger.error("Failed to notify team %s " %( self.team),
                     extra={
                        'team': self.team or self.partner,
                        'url': url,
                        'response': resp,
                        'content': content,
                        'data_sent':data_sent,
                    })

                Meter('http-callback-notification-error').inc()
            else:
                Meter('http-callback-notification-success').inc()
            return success, content
        except:
            logger.exception("Failed to send http notification ")
        return None, None

    def send_email(self, email_to):
        Meter('templated-emails-sent-by-type.teams.team-video-activity').inc()
        send_templated_email(email_to,
                _("New activity on your team video"),
                "teams/emails/new-activity.html",
                {
                    "video": self.video,
                    "event-name": self.event_name,
                    "team": self.team,
                    "laguage":self.language, 
                }
            )
