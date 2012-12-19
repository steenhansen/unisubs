from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.site_pages import video_page
from apps.webdriver_testing.site_pages import video_language_page
from apps.webdriver_testing import data_helpers
from apps.webdriver_testing.data_factories import UserFactory
from apps.webdriver_testing.editor_pages import subtitle_editor 
import codecs
import os

class TestCaseUntimedText(WebdriverTestCase):
    """TestSuite for uploading subtitles with untimed text.
    """
    
    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.user = UserFactory.create(username = 'user')
        self.video_pg = video_page.VideoPage(self)
        self.video_pg.log_in(self.user.username, 'password')
        self.test_video = data_helpers.create_video(self, 
            'http://www.example.com/upload_test.mp4')
        self.video_pg.open_video_page(self.test_video.video_id)
        self.subs_data_dir = os.path.join(os.getcwd(), 'apps', 
            'webdriver_testing', 'subtitle_data')

    def upload_and_verify(self, sub_file):
        """Upload the subtitle file and confirm subs are stored.

        Checking the subtitle count of the expected value vs the
        value in the database for the latest version of the lang.

        """
        self.video_pg.upload_subtitles('English', sub_file)
        subtitle_lang = self.test_video.subtitle_language('en') 
        self.assertEqual(43, subtitle_lang.get_subtitle_count())
        self.video_pg.open_page('videos/' + self.test_video.video_id + '/en/')


    def test_untimed__txt(self):
        """Upload untimed subs in a txt file.

        """
        test_file = 'Untimed_text.txt'
        sub_file = os.path.join(self.subs_data_dir, test_file) 
        self.upload_and_verify(sub_file)      
                
    def test_untimed__srt(self):
        """Upload untimed subs in a srt file.

        """
        test_file = 'Untimed_text.srt'
        sub_file = os.path.join(self.subs_data_dir, test_file) 
        self.upload_and_verify(sub_file)           

    def test_untimed__sbv(self):
        """Upload untimed subs in a sbv file.

        """
        test_file = 'Untimed_text.sbv'
        sub_file = os.path.join(self.subs_data_dir, test_file)       
        self.upload_and_verify(sub_file)     

    def test_untimed__ssa(self):
        """Upload untimed subs in a ssa file.

        """
        test_file = 'Untimed_text.ssa'
        sub_file = os.path.join(self.subs_data_dir, test_file)   
        self.upload_and_verify(sub_file)         

    def test_untimed__ttml(self):
        """Upload untimed subs in a ttml file.

        """
        test_file = 'Untimed_text.xml'
        sub_file = os.path.join(self.subs_data_dir, test_file)       
        self.upload_and_verify(sub_file)     

    def test_untimed__dfxp(self):
        """Upload untimed subs in a dfxp file.

        """
        test_file = 'Untimed_text.dfxp'
        sub_file = os.path.join(self.subs_data_dir, test_file)       
        self.upload_and_verify(sub_file)     

    def test_version__existing_translation(self):
        """On upload, create a new version and replace existing translation.

        Uploaded subs replace the existing version even if the existing
        version has subs created from it.
        """
        test_video3 = data_helpers.create_video(self, 
            'http://www.example.com/3.mp4')

        video_list = data_helpers.create_videos_with_fake_subs(self)
        test_file = 'Untimed_text.srt'
        sub_file = os.path.join(self.subs_data_dir, test_file)
        self.video_pg.open_video_page(test_video3.video_id)
     
        message = self.video_pg.upload_subtitles('Russian', sub_file)
        self.assertEqual(self.video_pg.UPLOAD_SUCCESS_TEXT, message)
        subtitle_lang = test_video3.subtitle_language('ru') 
        self.assertEqual(2, subtitle_lang.get_tip().version_number)

    def test__version__overwrite_existing(self):
        """On upload, create a new version and replace original transcription.

        Uploaded subs replace the existing version of original lang text.
        """
        test_video4 = data_helpers.create_video(self, 
            'http://www.example.com/4.mp4')

        video_list = data_helpers.create_videos_with_fake_subs(self)
        test_file = 'Untimed_text.srt'
        sub_file = os.path.join(self.subs_data_dir, test_file) 
        self.video_pg.open_video_page(test_video4.video_id)
      
        message = self.video_pg.upload_subtitles('Arabic', sub_file)
        self.assertEqual(self.video_pg.UPLOAD_SUCCESS_TEXT, message)
        sub_lang = test_video4.subtitle_language('ar')
        self.video_pg.page_refresh()
        subtitle_lang = test_video4.subtitle_language('ar') 
        self.assertEqual(2, subtitle_lang.get_tip().version_number)
    
    def test_upload__additional_translation(self):
        """Uploading a set of subs in a new language.

        New language is created as a new version.
        """
        test_video4 = data_helpers.create_video(self, 
            'http://www.example.com/4.mp4')

        video_list = data_helpers.create_videos_with_fake_subs(self)
        test_file = 'Untimed_text.srt'
        sub_file = os.path.join(self.subs_data_dir, test_file) 
        self.video_pg.open_video_page(test_video4.video_id)
      
        message = self.video_pg.upload_subtitles('Swedish', sub_file)
        self.assertEqual(self.video_pg.UPLOAD_SUCCESS_TEXT, message)
        self.video_pg.page_refresh()
        subtitle_lang = test_video4.subtitle_language('sv') 
        self.assertEqual(1, subtitle_lang.get_tip().version_number)

        self.assertEqual(43, subtitle_lang.get_subtitle_count() )

    def test_display__site(self):
        """Upload untimed subs verify content displayed on site lang page. 

        """
        video_language_pg = video_language_page.VideoLanguagePage(self)
        test_file = 'Untimed_text.srt'
        verification_file = os.path.join(self.subs_data_dir,'Untimed_lines.txt')
        expected_list = [line.strip() for line in codecs.open(
            verification_file, encoding='utf-8')]

        sub_file = os.path.join(self.subs_data_dir, test_file)       
        self.video_pg.upload_subtitles('English', sub_file)
        #Open the language page for the video and uploaded lang and compare
        video_language_pg.open_video_lang_page(
            self.test_video.video_id, 'en')
        displayed_list = video_language_pg.displayed_lines()

        self.assertEqual(expected_list, displayed_list)

    def test_edit(self):
        """Uploaded subtitles can be opened in the editor and saved.

        """
        video_language_pg = video_language_page.VideoLanguagePage(self)
        test_file = 'Untimed_text.srt'
        verification_file = os.path.join(self.subs_data_dir,'Untimed_lines.txt')
        expected_list = [line.strip() for line in codecs.open(
            verification_file, encoding='utf-8')]

        sub_file = os.path.join(self.subs_data_dir, test_file)       
        self.video_pg.upload_subtitles('English', sub_file)

        #Open the language page for the video and click Edit Subtitles 
        video_language_pg.open_video_lang_page(
            self.test_video.video_id, 'en')
        video_language_pg.edit_subtitles()
        sub_editor = subtitle_editor.SubtitleEditor(self)
        sub_editor.continue_past_help()
        editor_sub_list = sub_editor.subtitles_list()

        #Verify uploaded subs are displayed in the Editor
        #self.assertEqual(expected_list, editor_sub_list)
        typed_subs = sub_editor.edit_subs()

        sub_editor.save_and_exit()
        video_language_pg.open_video_lang_page(
            self.test_video.video_id, 'en')
        displayed_list = video_language_pg.displayed_lines()
        #Verify the edited text is in the sub list
        self.assertIn("Under the sea", displayed_list)

        #Verify the origal unedited text is still present in the sub list.
        self.assertIn(expected_list[9], displayed_list)

 
class TestCaseTimedText(WebdriverTestCase):
    """TestSuite for uploading subtitles with untimed text.
    """

    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.user = UserFactory.create(username = 'user')
        self.video_pg = video_page.VideoPage(self)
        self.video_pg.log_in(self.user.username, 'password')
        self.test_video = data_helpers.create_video(self, 
            'http://www.example.com/upload_test.mp4')
        self.video_pg.open_video_page(self.test_video.video_id)
        self.subs_data_dir = os.path.join(os.getcwd(), 'apps', 
            'webdriver_testing', 'subtitle_data')


    def upload_and_verify(self, sub_file, lang, lang_code, expected_count):
        """Upload the subtitle file and confirm subs are stored.

        Checking the subtitle count of the expected value vs the
        value in the database for the latest version of the lang.

        """
        self.video_pg.upload_subtitles(lang, sub_file)
        subtitle_lang = self.test_video.subtitle_language(lang_code)
        self.assertEqual(expected_count, subtitle_lang.get_subtitle_count())
        self.video_pg.open_page('videos/{0}/{1}/'.format(
            self.test_video.video_id, lang_code))



    def test_timed__txt(self):
        """Upload timed subs (en) in a txt file.

        """
        test_file = 'Timed_text.en.txt'
        sub_file = os.path.join(self.subs_data_dir, test_file)
        self.upload_and_verify( sub_file, 'English', 'en', 72 )

    def test_timed__srt(self):
        """Upload timed subs (sv) in a srt file.

        """
        test_file = 'Timed_text.sv.srt'
        sub_file = os.path.join(self.subs_data_dir, test_file)
        self.upload_and_verify( sub_file, 'Swedish', 'sv', 72 )
       

    def test_timed__sbv(self):
        """Upload timed subs (zh-cn) in a sbv file.

        """
        test_file = 'Timed_text.zh-cn.sbv'
        sub_file = os.path.join(self.subs_data_dir, test_file)       
        self.upload_and_verify(sub_file, 'Chinese, Simplified', 'zh-cn', 243 )

    def test_timed__ssa(self):
        """Upload timed subs (hu) in a ssa file.

        """
        test_file = 'Timed_text.hu.ssa'
        sub_file = os.path.join(self.subs_data_dir, test_file)       
        self.upload_and_verify(sub_file, 'Hungarian', 'hu', 243 )


    def test_timed__ttml(self):
        """Upload timed subs (ar) in a ttml file.

        """
        test_file = 'Timed_text.ar.xml'
        sub_file = os.path.join(self.subs_data_dir, test_file)       
        self.upload_and_verify(sub_file, 'Arabic', 'ar', 243 )

    def test_timed__dfxp(self):
        """Upload timed subs (sv) in a dfxp file.

        """
        test_file = 'Timed_text.sv.dfxp'
        sub_file = os.path.join(self.subs_data_dir, test_file)       
        self.upload_and_verify(sub_file, 'Swedish', 'sv', 72 )




