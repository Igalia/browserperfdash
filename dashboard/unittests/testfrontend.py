from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait


class FrontEndTestCase(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.PhantomJS()

    def test_angular_on_jasmine(self):
        self.browser.get(self.live_server_url + '/tests/')
        WebDriverWait(self.browser, 10).until(
            lambda x: x.find_element_by_class_name("jasmine-failures"))
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_xpath("//div[@class='jasmine-failures']/div")