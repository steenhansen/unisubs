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

import logging

from django.db import models
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.utils import translation

from videos.models import VIDEO_TYPE, VIDEO_TYPE_YOUTUBE
from .videos.types import (
    video_type_registrar, UPDATE_VERSION_ACTION, DELETE_LANGUAGE_ACTION
)
from teams.models import Team
from auth.models import CustomUser as User

from utils.metrics import Meter

logger = logging.getLogger(__name__)

# for now, they kind of match
ACCOUNT_TYPES = VIDEO_TYPE
AMARA_CREDIT = translation.ugettext("Subtitles by the Amara.org community")
AMARA_DESCRIPTION_CREDIT = translation.ugettext(
    "Help us caption and translate this video on Amara.org")


def youtube_sync(video, language):
    """
    Used on debug page for video.

    Simplified version of what's found in
    ``ThirdPartyAccount.mirror_on_third_party``.  It doesn't bother checking if
    we should be syncing this or not.  Only does the new Youtube/Amara
    integration syncing.
    """
    version = language.get_tip()

    always_push_account = ThirdPartyAccount.objects.always_push_account()

    for vurl in video.videourl_set.all():
        vt = video_type_registrar.video_type_for_url(vurl.url)

        try:
            vt.update_subtitles(version, always_push_account)
            Meter('youtube.push.success').inc()
        except:
            Meter('youtube.push.fail').inc()
            logger.error('Always pushing to youtoube has failed.', extra={
                'video': video.video_id,
                'vurl': vurl.pk
            })
        finally:
            Meter('youtube.push.request').inc()


def check_authorization(video):
    """
    Make sure that a video can have its subtitles synced to Youtube.  This
    doesn't take into account any language/version information.

    Return a tuple of (is_authorized, ignore_new_syncing_logic).
    """
    team_video = video.get_team_video()
    ignore_new_syncing_logic = False

    if team_video:
        team = team_video.team
        has_linked_youtube_account = team.third_party_accounts.filter(
                type=VIDEO_TYPE_YOUTUBE).exists()
        if has_linked_youtube_account:
            # Ignore the new syncing logic.  Use the linked Youtube account
            # to publish subtitles to Youtube.
            ignore_new_syncing_logic = True
        else:
            # The assumption is that it's the partner's official Youtube
            # account and they don't want it messed up with strange subs.
            return False, None
    else:
        # If a video isn't part of a team but the video's Youtube URL is linked
        # to a team third party account, we don't sync to Youtube.
        yt_url = video.videourl_set.filter(type=VIDEO_TYPE_YOUTUBE)
        if yt_url.exists():
            usernames = [url.owner_username for url in yt_url]
            linked_accounts = ThirdPartyAccount.objects.filter(
                    username__in=usernames)

            if linked_accounts.exists():
                if any(a.is_team_account for a in linked_accounts):
                    return False, None

    return True, ignore_new_syncing_logic


def can_be_synced(version):
    """
    Return whether a subtitle version can be synced to Youtube.

    A version must be public, synced and complete.

    TODO: take visibility into account
    """
    if version:
        if not version.is_public() or not version.is_synced():
            # We can't mirror unsynced or non-public versions.
            return False

        if not version.subtitle_language.subtitles_complete:
            # Don't sync incomplete languages
            return False

    return True


def translate_string(string, language='en'):
    """
    If a translation for the specified language doesn't exist, return the
    English version.
    """
    cur_language = translation.get_language()
    try:
        translation.activate(language)
        text = translation.ugettext(string)
    finally:
        translation.activate(cur_language)
    return text


def get_amara_credit_text(language='en'):
    return translate_string(AMARA_CREDIT, language)


def translate_string(string, language='en'):
    """
    If a translation for the specified language doesn't exist, return the
    English version.
    """
    cur_language = translation.get_language()
    try:
        translation.activate(language)
        text = translation.ugettext(string)
    finally:
        translation.activate(cur_language)
    return text


def get_amara_credit_text(language='en'):
    return translate_string(AMARA_CREDIT, language)


def add_amara_description_credit(old_description, video_url, language='en'):
    """
    Prepend the credit to the existing description.
    """
    credit = translate_string(AMARA_DESCRIPTION_CREDIT, language)

    if old_description.startswith(credit):
        return old_description

    return "%s: %s\n\n%s" % (
        credit,
        video_url,
        old_description or ""
    )


class ThirdPartyAccountManager(models.Manager):

    def always_push_account(self):
        """
        Get the ThirdPartyAccount that is able to push to any video on Youtube.
        Raise ``ImproperlyConfigured`` if it can't be found.
        """
        username = getattr(settings, 'YOUTUBE_ALWAYS_PUSH_USERNAME')

        try:
            return self.get(username=username)
        except ThirdPartyAccount.DoesNotExist:
            raise ImproperlyConfigured("Can't find youtube account")

    def mirror_on_third_party(self, video, language, action, version=None):
        """
        Does the specified action (video.types.UPDATE_VERSION_ACTION or
                                   video.types.DELETE_LANGUAGE_ACTION) 
        on the original account (e.g. Youtube video).
        For example, to update a given version to Youtube:
             ThirdPartyAccountManager.objects.mirror_on_third_party(
                       video, language, "update_subtitles", version)
        For deleting, we only delete languages, so it should be 
              ThirdPartyAccountManager.objects.mirror_on_third_party(
                        video, language, "delete_subtitles")
        This method is 'safe' to call, meaning that we only do syncing if there 
        are matching third party credentials for this video.
        The update will only be done if the version is synced
        """
        if action not in [UPDATE_VERSION_ACTION, DELETE_LANGUAGE_ACTION]:
            raise NotImplementedError(
                "Mirror to third party does not support the %s action" % action)

        if not version and action == UPDATE_VERSION_ACTION:
            raise ValueError("You need to pass a version when updating subs")

        if not can_be_synced(version):
            return

        is_authorized, ignore_new_syncing_logic = check_authorization(video)

        if not is_authorized:
            return

        try:
            rule = YoutubeSyncRule.objects.all()[0]
            should_sync = rule.should_sync(video)
            always_push_account = self.always_push_account()
        except IndexError:
            should_sync = False

        for vurl in video.videourl_set.all():
            already_updated = False
            vt = video_type_registrar.video_type_for_url(vurl.url)

            if should_sync:
                try:
                    vt.update_subtitles(version, always_push_account)
                    already_updated = True
                    Meter('youtube.push.success').inc()
                except:
                    Meter('youtube.push.fail').inc()
                    logger.error('Pushing to youtoube has failed.', extra={
                        'video': video.video_id,
                        'vurl': vurl.pk
                    })
                finally:
                    Meter('youtube.push.request').inc()

            username = vurl.owner_username

            if not username:
                continue
            try:
                account = ThirdPartyAccount.objects.get(type=vurl.type, username=username)
            except ThirdPartyAccount.DoesNotExist:
                continue

            if hasattr(vt, action):
                if action == UPDATE_VERSION_ACTION and not already_updated:
                    vt.update_subtitles(version, account)
                elif action == DELETE_LANGUAGE_ACTION:
                    vt.delete_subtitles(language, account)


class ThirdPartyAccount(models.Model):
    """
    Links a third party account (e.g. YouTube's') to a certain video URL
    This allows us to push changes in Unisubs back to that video provider.
    The user links a video on unisubs to his youtube account. Once edits to
    any languages are done, we push those back to Youtube.
    For know, this only supports Youtube, but nothing is stopping it from
    working with others.
    """
    type = models.CharField(max_length=10, choices=ACCOUNT_TYPES)
    # this is the third party account user name, eg the youtube user
    username  = models.CharField(max_length=255, db_index=True, 
                                 null=False, blank=False)
    oauth_access_token = models.CharField(max_length=255, db_index=True, 
                                          null=False, blank=False)
    oauth_refresh_token = models.CharField(max_length=255, db_index=True,
                                           null=False, blank=False)
    
    objects = ThirdPartyAccountManager()
    
    class Meta:
        unique_together = ("type", "username")

    def __unicode__(self):
        return '%s - %s' % (self.get_type_display(), self.username)

    @property
    def is_team_account(self):
        return self.teams.exists()

    @property
    def is_individual_account(self):
        return self.users.exists()


class YoutubeSyncRule(models.Model):
    """
    An instance of this class determines which Youtube videos should be synced
    back to Youtube via the new integration.

    There should only ever be one instance of this class in the database.

    You should run a query and then call it like this:

        rule = YoutubeSyncRule.objects.all()[0]
        rule.should_sync(video)

    Where ``video`` is a ``videos.models.Video`` instance.

    ``team`` should be a comma-separated list of team slugs that you want to
    sync.  ``user`` should be a comma-separated list of usernames of users
    whose videos should be synced.  ``video`` is a list of video ids of
    videos that should be synced.

    You can also specify a wildcard "*" to any of the above to match any teams,
    any users, or any videos.
    """
    team = models.TextField(default='', blank=True,
            help_text='Comma separated list of slugs')
    user = models.TextField(default='', blank=True,
            help_text='Comma separated list of usernames')
    video = models.TextField(default='', blank=True,
            help_text='Comma separated list of video ids')

    def __unicode__(self):
        return 'Youtube sync rule'

    def team_in_list(self, team):
        if not team:
            return False
        teams = self.team.split(',')
        if '*' in teams:
            return True
        return team in teams

    def user_in_list(self, user):
        if not user:
            return False

        users = self.user.split(',')

        if '*' in users:
            return True
        return user.username in users

    def video_in_list(self, pk):
        pks = self.video.split(',')
        if '*' in pks:
            return True
        if len(pks) == 1 and pks[0] == '':
            return False
        return pk in pks

    def should_sync(self, video):
        tv = video.get_team_video()
        team = None
        if tv:
            team = tv.team.slug

        return self.team_in_list(team) or \
                self.user_in_list(video.user) or \
                self.video_in_list(video.video_id)

    def _clean(self, name):
        if name not in ['team', 'user']:
            return
        field  = getattr(self, name)
        values = set(field.split(','))
        values = [v for v in values if v != '*']
        if len(values) == 1 and values[0] == '':
            return []
        return values

    def clean(self):
        teams = self._clean('team')
        users = self._clean('user')

        if len(teams) != Team.objects.filter(slug__in=teams).count():
            raise ValidationError("One or more teams not found")

        if len(users) != User.objects.filter(username__in=users).count():
            raise ValidationError("One or more users not found")
