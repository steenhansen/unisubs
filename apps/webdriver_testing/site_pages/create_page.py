#!/usr/bin/env python

import time
from unisubs_page import UnisubsPage


class CreatePage(UnisubsPage):
    """
     Video Page contains the common elements in the video page.
    """

    _SINGLE_URL_ENTRY_BOX = "input.main_video_form_field"
    _INPUT_PREFOCUS = "input#submit_video_field.prefocus"
    _URL = "videos/create"
    _SUBMIT_BUTTON = "form.main_video_form button.green_button"
    _MULTI_SUBMIT_LINK = " div#submit_multiple_toggle a#btn_submit_multiple_toggle.toogle-create-form"
    _YOUTUBE_USER_FIELD = "li input#id_usernames"
    _YOUTUBE_PAGE_FIELD = "li input#id_youtube_user_url"
    _FEED_URL = "li input#id_feed_url"
    _SAVE_OPTION = "div#submit_multiple_videos form#bulk_create ul li input#id_save_feed"
    _SUBMIT_MULTI = "div#submit_multiple_videos form#bulk_create button.green_button"
    _HIDE_MULTI = "div#submit_multiple_toggle"
    _SUBMIT_ERROR = "ul.errorlist li"

    def open_create_page(self):
        print self._URL
        self.open_page(self._URL)

    def submit_video(self, video_url):
        self.wait_for_element_present(self._INPUT_PREFOCUS)
        self.click_by_css("div h2.main_heading")
        self.clear_text(self._SINGLE_URL_ENTRY_BOX)
        print "Entering the url: %s" % self._URL
        self.type_by_css(self._SINGLE_URL_ENTRY_BOX, video_url)
        self.click_by_css(self._SUBMIT_BUTTON)
        time.sleep(3)

    def _open_multi_submit(self):
        self.click_by_css(self._MULTI_SUBMIT_LINK)
        self.page_down(self._HIDE_MULTI)
        self.wait_for_element_present(self._YOUTUBE_USER_FIELD)

    def submit_youtube_users_videos(self, youtube_usernames, save=False):
        """Submit 1 or several youtube user names.
        Type 1 or several youtube user names in hte Youtube usernames field.

        """
        self._open_multi_submit()
        for name in youtube_usernames:
            self.type_by_css(self._YOUTUBE_USER_FIELD, name)
        if save == True:
            self.click_by_css(self._SAVE_OPTION)
        self.click_by_css(self._SUBMIT_MULTI)
        time.sleep(3)

    def submit_youtube_user_page(self, youtube_user_url, save=False):
        """Submit videos from youtube user page url.

        Enter a youtube user's page url.
        """
        self._open_multi_submit()
        self.type_by_css(self._YOUTUBE_PAGE_FIELD, youtube_user_url)
        if save == True:
            self.click_by_css(self._SAVE_OPTION)
        self.click_by_css(self._SUBMIT_MULTI)
        time.sleep(3)

    def submit_feed_url(self, feed_url, save=False):
        """Submit videos from a supported feed type.

        """
        self._open_multi_submit()
        self.type_by_css(self._FEED_URL, feed_url)
        if save == True:
            self.click_by_css(self._SAVE_OPTION)
        self.click_by_css(self._SUBMIT_MULTI)

    def multi_submit_successful(self):
        self.wait_for_element_present(self._SUCCESS_MESSAGE)
        if self.is_text_present(self._SUCCESS_MESSAGE,
                                u"The videos are being added in the background. "
                                u"If you are logged in, you will receive a message when it's done"):
            return True
        else:
            print self.get_text_by_css(self._SUCCESS_MESSAGE)

    def multi_submit_failed(self):
        self.wait_for_element_present(self._ERROR_MESSAGE)
        if self.is_element_present(self._ERROR_MESSAGE):
            return True

    def submit_success(self, expected_error=False):
        if expected_error == False and self.is_element_present(self._SUBMIT_ERROR):
            error_msg = self.get_text_by_css(self._SUBMIT_ERROR)
            raise ValueError("Submit failed: site says %s" % error_msg)
        elif expected_error == True and self.is_element_present(self._SUBMIT_ERROR):
            return error_msg
        else:
            return True
        #FIXME - you can do better verfication than this
