# -*- coding: utf-8 -*-
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

from apps.webdriver_testing.site_pages import create_page
from apps.webdriver_testing.webdriver_base import WebdriverTestCase


class TestCaseVideosCreateVideos(WebdriverTestCase):
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.create_pg = create_page.CreatePage(self)
        self.create_pg.open_create_page()

    def test_create__youtube(self):
        """Add a youtube video.

        """
        url = 'http://www.youtube.com/watch?v=WqJineyEszo'
        self.create_pg.submit_video(url)
        self.assertTrue(self.create_pg.submit_success())


    def test_create__brightcove(self):
        """Add a brightcove video.

        """
        #Brightcove support added under this ticket: 
        #https://unisubs.sifterapp.com/issues/1648
        url = 'http://bcove.me/8yxc6sxy'
        self.create_pg.submit_video(url)
        self.assertTrue(self.create_pg.submit_success())

    def test_create__dailymotion(self):
        """Add a dailymotion video.

        """

        url = ('http://www.dailymotion.com/video/'
               'xlh9h1_fim-syndicat-des-apiculteurs-de-metz-environs_news')
        self.create_pg.submit_video(url)
        self.assertTrue(self.create_pg.submit_success())

    def test_create__vimeo(self):
        """Add a vimeo video.

        """

        url = "http://vimeo.com/26487510"
        self.create_pg.submit_video(url)
        self.assertTrue(self.create_pg.submit_success())

    def test_create__ogg(self):
        """Add an ogg video video.

        """

        url = "http://qa.pculture.org/amara_tests/Birds_short.oggtheora.ogg"
        self.create_pg.submit_video(url)
        self.assertTrue(self.create_pg.submit_success())

    def test_create__mp4(self):
        """Add a an mp4 video.

        """

        url = "http://qa.pculture.org/amara_tests/Birds_short.mp4"
        self.create_pg.submit_video(url)
        self.assertTrue(self.create_pg.submit_success())

    def test_create__blip_flv(self):
        """Add a blip video.

        """

        url = "http://blip.tv/file/get/Linuxconfau-LightningTalks606.flv"
        self.create_pg.submit_video(url)
        self.assertTrue(self.create_pg.submit_success())

    def test_create__webm(self):
        """Add a webM video.

        """

        url = "http://qa.pculture.org/amara_tests/Birds_short.webmsd.webm"
        self.create_pg.submit_video(url)
        self.assertTrue(self.create_pg.submit_success())

    def test_create__youtu_be_url(self):
        """Add a youtube video with youtu.be url.

        """

        url = "http://youtu.be/BXMPp0TLSEo"
        self.create_pg.submit_video(url)
        self.assertTrue(self.create_pg.submit_success())


class TestCaseAddFeeds(WebdriverTestCase):
    """Test Suite for adding video feeds.

    """
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.create_pg = create_page.CreatePage(self)
        self.create_pg.open_create_page()

    def test_feed__youtube_user(self):
        """Add a youtube user feed

        """

        youtube_user = 'croatiadivers'
        self.create_pg.submit_youtube_users_videos(youtube_user, save=True)
        self.assertTrue(self.create_pg.multi_submit_successful())

    def test_feed__youtube_user_url(self):
        """Add a youtube user url feed

        """

        url = "http://www.youtube.com/user/jdragojevic"
        self.create_pg.submit_youtube_user_page(url, save=True)
        self.assertTrue(self.create_pg.multi_submit_successful())

    def test_feed__vimeo(self):
        """Add a vimeo feed

        """

        url = "http://vimeo.com/jeroenhouben/videos/rss"
        self.create_pg.submit_feed_url(url)
        self.assertTrue(self.create_pg.multi_submit_successful())

    def test_feed__dailymotion(self):
        """Add a dailymotion feed

        """

        url = "http://www.dailymotion.com/rss/user/WildFilmsIndia/1"
        self.create_pg.submit_feed_url(url)
        self.assertTrue(self.create_pg.multi_submit_successful())

    def test_feed__dailymotion_large(self):
        """Add a v. large dailymotion feed

        """

        self.skipTest("This is just too slow, and probably not that necessary")
        url = "http://www.dailymotion.com/rss/user/LocalNews-GrabNetworks/1"
        self.create_pg.submit_feed_url(url)
        self.assertTrue(self.create_pg.multi_submit_successful())

    def test_feed__blip(self):
        """Add a blip feed

        """

        url = "http://blip.tv/stitchnbitch/rss"
        self.create_pg.submit_feed_url(url)
        self.assertTrue(self.create_pg.multi_submit_successful())

    def test_feed__blip_workaround(self):
        """Add a individual blip video as feed (blip workaround)

        """

        url = ('http://blip.tv/cord-cutters/'
               'cord-cutters-sync-mobile-media-with-miro-4-5280931?skin=rss')
        self.create_pg.submit_feed_url(url)
        self.assertTrue(self.create_pg.multi_submit_successful())

    def test_feed__youtube_feed(self):
        """Add a youtube feed

        """

        url = "http://gdata.youtube.com/feeds/api/users/janetefinn/uploads"
        self.create_pg.submit_feed_url(url)
        self.assertTrue(self.create_pg.multi_submit_successful())
