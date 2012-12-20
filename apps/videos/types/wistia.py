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



from base import VideoType, VideoTypeError
import httplib
from django.utils import simplejson as json
import re
from django.utils.translation import ugettext_lazy as _

# apps/videos/types/wistia.py
import logging



DAILYMOTION_REGEX = re.compile(r'https?://(?:[^/]+[.])?dailymotion.com/video/(?P<video_id>[-0-9a-zA-Z]+)(?:_.*)?')

  
#WISTIA_REGEX = re.compile(r'https?://([^/]+\.)?(hootsuite\.wistia\.com|wi\.st)/(medias|embed)/(iframe/)?(?P<video_id>\d+)')

#WISTIA_REGEX = re.compile(r'https?://([^/]+\.)?(hootsuite\.wistia\.com)/(medias|embed)/(iframe/)?(?P<video_id>[-0-9a-zA-Z]+)')

#http://hootsuite.wistia.com/medias/17bvist1ia
WISTIA_REGEX = re.compile(r'http://hootsuite\.wistia\.com/embed/iframe/([-0-9a-zA-Z]+)')


class WistiaVideoType(VideoType):


    abbreviation = 'W'
    name = 'Wistia.com'   
    site = 'Wistia.com'

    def __init__(self, url):
        self.url = url
        self.videoid = self.get_video_id(url)

    @property
    def video_id(self):
        return self.videoid
#   http://fast.wistia.com/embed/iframe/ivaqrc8ue8
    def convert_to_video_hootsuite(self):
        return 'http://hootsuite.wistia.com/embed/iframe/%s' % self.video_id

    @classmethod
    def video_url(cls, obj):
        return 'http://hootsuite.wistia.com/embed/iframe/%s' % obj.videoid

    @classmethod
    def matches_video_url(cls, url):
 
     #   import logging
        log = logging.getLogger('myapp')
        hdlr = logging.FileHandler('/opt/apps/vagrant/unisubs/myapp.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        log.addHandler(hdlr) 
        log.setLevel(logging.WARNING)
       # log.error('ssss in ') 

        video_id = cls.get_video_id(url)
        #log.error('wistia - matches_video_url ' + video_id )
        #log.error('ssss out ') 
        if video_id:
          #  log.error('return true')
            return True
       # log.error('return false')
        return False

    def create_kwars(self):
        return {'videoid': self.video_id}

    def set_values(self, video_obj):

        log = logging.getLogger('myapp')
        hdlr = logging.FileHandler('/opt/apps/vagrant/unisubs/myapp.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        log.addHandler(hdlr) 
        log.setLevel(logging.WARNING)
        log.error( 'yep3' )


        metadata = self.get_metadata(self.video_id)
        #video_obj.description = metadata.get('description', u'')
        #video_obj.title = metadata.get('title', '')
        #video_obj.thumbnail = metadata.get('thumbnail_url') or ''
        #return video_obj

    @classmethod
    def get_video_id(cls, video_url):

        log = logging.getLogger('myapp')
        hdlr = logging.FileHandler('/opt/apps/vagrant/unisubs/myapp.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        log.addHandler(hdlr) 
        log.setLevel(logging.WARNING)
 
     #   log.error('cls.format_url ' + cls.format_url(video_url) )

     #   log.error('nnn')

        match = WISTIA_REGEX.match(cls.format_url(video_url))
 
      #  log.error(cls.format_url(video_url) )
      #  log.error('qqqq')


        #log.error('wistia - get_video_id a ' + match.group(0) )
       # log.error('wistia - get_video_id B ' + match.group(1) )
      #  log.error('wistia - get_video_id c ' + match.group(2) )
      #  log.error('wistia - get_video_id D ' + match.group(3) )
     #   log.error('wistia - get_video_id e ' + match.group(4) )
        return match and match.group(1)

   

    @classmethod
    def get_metadata(cls, video_id):
        #FIXME: get_metadata is called twice: in matches_video_url and set_values
        log = logging.getLogger('myapp')
        hdlr = logging.FileHandler('/opt/apps/vagrant/unisubs/myapp.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        log.addHandler(hdlr) 
        log.setLevel(logging.WARNING)
        log.error( 'yep' )
# WISTIA_API_URL = 'http://fast.wistia.com/oembed?url=http://hootsuite.wistia.com/medias/'
        conn = httplib.HTTPConnection("fast.wistia.com/oembed?url=http://hootsuite.wistia.com/medias/")
        conn.request("GET",  video_id)
        try:
            response = conn.getresponse()
            body = response.read()
            log.error(body)
            try:
                return json.loads(body)
            except json.JSONDecodeError:
                raise VideoTypeError(_(u'Video is unavailable'))
        except httplib.BadStatusLine:
            return {}

