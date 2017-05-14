from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait


class FrontEndTestCase(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.PhantomJS()

    def test_angular_on_jasmine(self):
        """
        Load the page IP/tests/ correctly, and check if we have a 'success' on
        all tests, also verify that there is no failures
        """
        self.browser.get(self.live_server_url + '/tests/')
        WebDriverWait(self.browser, 10).until(
            lambda x: x.find_element_by_class_name("jasmine-alert"))
        # Check if there is a success span in jasmine-alert
        try:
            self.browser.find_element_by_xpath("//span[@class='jasmine-bar jasmine-passed']")
        except NoSuchElementException:
            self.fail("Test success message not found in jasmine-alert")

        # Verify that there are no failures in jasmine-failures
        WebDriverWait(self.browser, 10).until(
            lambda x: x.find_element_by_class_name("jasmine-failures"))
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_xpath("//div[@class='jasmine-failures']/div")