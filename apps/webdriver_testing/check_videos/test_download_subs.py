from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.site_pages import video_page
from apps.webdriver_testing.site_pages import video_language_page
from apps.webdriver_testing import data_helpers
from apps.webdriver_testing.data_factories import UserFactory
from apps.webdriver_testing.data_factories import VideoUrlFactory
from apps.webdriver_testing.editor_pages import subtitle_editor 
import codecs
import os

 
class TestCaseDownloadSubs(WebdriverTestCase):
    """TestSuite for download subtitles from the video's lanugage page   """

    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.user = UserFactory.create(username = 'user')
        self.video_language_pg = video_language_page.VideoLanguagePage(self)
        self.video_language_pg.log_in(self.user.username, 'password')
        self.subs_data_dir = os.path.join(os.getcwd(), 'apps', 
            'webdriver_testing', 'subtitle_data')

    def _add_video_and_subs(self, sub_file, lang_code, title):
        """Create the test videos and add subtitles to it.
  
        """
        video = VideoUrlFactory(
            url = 'http://example.unisubs.com/download-test.mp4',
            video__title = title
            ).video
        print video.video_id

        data = {'language_code': lang_code,
               'video_language': lang_code,
               'video': video.pk,
               'draft': open(sub_file),
               'is_complete': True
               }
        data_helpers.upload_subs(self, video, data)
        print video.video_id
        return video

    def _download_filename(self, title, lang_code, output):
        dl_filename = '{0}.{1}.{2}'.format(title.replace(' ', '_'), 
                                           lang_code,
                                           output.lower())
        return dl_filename

    def _check_download_subtitles(self, video, lang_code, download_format):

        #Open the videos language page
        self.video_language_pg.open_video_lang_page(video.video_id, lang_code)

        #Find the link and make a request to get the header.
        dl_link = self.video_language_pg.download_link(download_format)
        dl_header = self.video_language_pg.check_download_link(dl_link)

        #Get the expected output filename and check it matches the link from the page.
        dl_filename = self._download_filename(video.title, lang_code, download_format)
        self.assertEqual("attachment; filename*=UTF-8''%s" % dl_filename,
                          dl_header['content-disposition'])

    def test_download__txt(self):
        """Download subs in txt format.

        """

        #Specify subtitle file, language and download formats.
        test_file = 'Timed_text.en.txt'
        video_title = 'English subs txt format download'
        download_format = 'TXT'
        lang_code = 'en'
        sub_file = os.path.join(self.subs_data_dir, test_file)

        #Create a video and upload subtitles
        test_video = self._add_video_and_subs(sub_file, lang_code, video_title)

        #Open the video's language page, and verify the download link is valid 
        #and outputs the expected data and file format.
        self._check_download_subtitles(test_video, lang_code, download_format)

    def test_download__srt(self):
        """Download subs (sv) in a srt file.

        """
        test_file = 'Timed_text.sv.srt'
        video_title = 'Swedish subs srt format download'
        download_format = 'SRT'
        lang_code = 'sv'
        sub_file = os.path.join(self.subs_data_dir, test_file)

        #Create a video and upload subtitles
        test_video = self._add_video_and_subs(sub_file, lang_code, video_title)

        #Open the video's language page, and verify the download link is valid 
        #and outputs the expected data and file format.
        self._check_download_subtitles(test_video, lang_code, download_format)

    def test_download__ted(self):
        """Download subs (sv) in a srt file.

        """
        test_file = 'Timed_text.sv.srt'
        video_title = 'Swedish subs TED format download'
        download_format = 'TED'
        lang_code = 'sv'
        sub_file = os.path.join(self.subs_data_dir, test_file)

        #Create a video and upload subtitles
        test_video = self._add_video_and_subs(sub_file, lang_code, video_title)

        #Open the video's language page, and verify the download link is valid 
        #and outputs the expected data and file format.
        self._check_download_subtitles(test_video, lang_code, download_format)
       

    def test_download__sbv(self):
        """Download subs (zh-cn) as a sbv file.

        """
        test_file = 'Timed_text.zh-cn.sbv'
        video_title = 'Chinese subs sbv format download'
        download_format = 'SBV'
        lang_code = 'zh-cn'
        sub_file = os.path.join(self.subs_data_dir, test_file)

        #Create a video and upload subtitles
        test_video = self._add_video_and_subs(sub_file, lang_code, video_title)

        #Open the video's language page, and verify the download link is valid 
        #and outputs the expected data and file format.
        self._check_download_subtitles(test_video, lang_code, download_format)

    def test_download__json(self):
        """Download subs (zh-cn) as a json file.

        """
        test_file = 'Timed_text.zh-cn.sbv'
        video_title = 'Chinese subs sbv format download'
        download_format = 'JSON'
        lang_code = 'zh-cn'
        sub_file = os.path.join(self.subs_data_dir, test_file)

        #Create a video and upload subtitles
        test_video = self._add_video_and_subs(sub_file, lang_code, video_title)

        #Open the video's language page, and verify the download link is valid 
        #and outputs the expected data and file format.
        self._check_download_subtitles(test_video, lang_code, download_format)



    def test_download__ssa(self):
        """Upload timed subs (hu) in a ssa file.

        """
        test_file = 'Timed_text.hu.ssa'
        video_title = 'Hungarian subs ssa format download'
        sub_file = os.path.join(self.subs_data_dir, test_file)       
        download_format = 'SSA'
        lang_code = 'hu'
        sub_file = os.path.join(self.subs_data_dir, test_file)

        #Create a video and upload subtitles
        test_video = self._add_video_and_subs(sub_file, lang_code, video_title)

        #Open the video's language page, and verify the download link is valid 
        #and outputs the expected data and file format.
        self._check_download_subtitles(test_video, lang_code, download_format)


    def test_download__ass(self):
        """Upload timed subs (hu) in an ass file.

        """
        test_file = 'Timed_text.hu.ssa'
        video_title = 'Hungarian subs ass format download'
        sub_file = os.path.join(self.subs_data_dir, test_file)       
        download_format = 'ASS'
        lang_code = 'hu'
        sub_file = os.path.join(self.subs_data_dir, test_file)

        #Create a video and upload subtitles
        test_video = self._add_video_and_subs(sub_file, lang_code, video_title)

        #Open the video's language page, and verify the download link is valid 
        #and outputs the expected data and file format.
        self._check_download_subtitles(test_video, lang_code, download_format)


    def test_download__xml(self):
        """Download subs (hu) in an xml file.

        """
        test_file = 'Timed_text.hu.ssa'
        video_title = 'Hungarian subs xml format download'
        download_format = 'XML'
        lang_code = 'hu'
        sub_file = os.path.join(self.subs_data_dir, test_file)       

        #Create a video and upload subtitles
        test_video = self._add_video_and_subs(sub_file, lang_code, video_title)

        #Open the video's language page, and verify the download link is valid 
        #and outputs the expected data and file format.
        self._check_download_subtitles(test_video, lang_code, download_format)


    def test_timed__dfxp(self):
        """ Download subs (sv) in a dfxp file.

        """
        test_file = 'Timed_text.sv.srt'
        video_title = 'Swedish subs dxfp format download'
        download_format = 'DFXP'
        lang_code = 'sv'
        sub_file = os.path.join(self.subs_data_dir, test_file)

        #Create a video and upload subtitles
        test_video = self._add_video_and_subs(sub_file, lang_code, video_title)

        #Open the video's language page, and verify the download link is valid 
        #and outputs the expected data and file format.
        self._check_download_subtitles(test_video, lang_code, download_format)





