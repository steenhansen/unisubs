from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.site_pages import watch_page
from apps.webdriver_testing.data_factories import UserFactory 
from apps.webdriver_testing import data_helpers
from django.core import management
import datetime


class TestCaseLogin(WebdriverTestCase):
    """TestSuite for site video searches.

    """

    def setUp(self):
        WebdriverTestCase.setUp(self)
        self.user = UserFactory.create(username='tester')
        self.watch_pg = watch_page.WatchPage(self)

    def test_login__site(self):
        """Open the site and login as site user.

        """
        self.watch_pg.open_watch_page()
         
        
