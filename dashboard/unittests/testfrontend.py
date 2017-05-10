from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


class FrontEndTestCase(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.PhantomJS()
        self.browser.implicitly_wait(10)

    def test_angular_on_jasmine(self):
        self.browser.get(self.live_server_url + '/tests/')
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_xpath("//div[@class='jasmine-failures']/div")