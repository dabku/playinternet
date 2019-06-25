from time import time, sleep
import logging
from os import makedirs, path, listdir, remove
import sys
from selenium.common import exceptions as selenium_exceptions


class Play24:
    def __init__(self, login, password, selenium_driver):
        self.prepare_screenshot_dir()
        self._sd = selenium_driver
        self.credentials = {
            'login': login,
            'password': password
        }
        self.login_url = 'https://24.play.pl/'
        self.billing_url = 'https://24.play.pl/Play24/Billing'

    def prepare_screenshot_dir(self, files_to_retain = 10):

        script_dir = path.dirname(path.realpath(sys.argv[0]))
        if not path.exists(path.join(script_dir, 'screenshots')):
            makedirs(path.join(script_dir, 'screenshots'))
            return
        list_of_files = listdir(path.join(script_dir, 'screenshots'))
        full_path_files = [path.join(script_dir, 'screenshots', x) for x in list_of_files]
        sorted_files = sorted(full_path_files, key=path.getctime)
        for i in range(len(sorted_files) - files_to_retain):
            remove(sorted_files[i])

    def save_screenshot(self):
        script_dir = path.dirname(path.realpath(sys.argv[0]))
        filename = path.join(script_dir,'screenshots','failed_{}.png'.format(time()))
        self._sd.save_screenshot(filename)
        logging.error('saved screenshot {}'.format(filename))

    def scrape_current_month_usage(self):
        try:
            self.login()
            self.navigate_to_billing()
            self.set_current_period()
            data_usage = self.get_data_usage()
        except Exception as e:
            self.save_screenshot()
            logging.error('Got exception {}'.format(e.msg))

            raise
        else:
            return data_usage

    def login(self):
        logging.debug('Logging in, opening logging page')
        self._sd.get(self.login_url)
        logging.debug('setting credentials')
        username_input = self._sd.find_element_by_id("IDToken1")
        username_input.send_keys(self.credentials['login'])
        passwordinput = self._sd.find_element_by_id("IDToken2")
        passwordinput.send_keys(self.credentials['password'])
        login_button = self._sd.find_element_by_name("Login.Submit")
        logging.debug('submitting credentials')
        login_button.click()

    def navigate_to_billing(self):
        logging.debug('Navigating to billing url')
        self._sd.get(self.billing_url)

    def set_current_period(self):
        logging.debug('Changing billing period')
        radio_button = self._sd.find_element_by_xpath(
            "//fieldset[contains(@class,'period')]//input[@value='currentBillPeriod']")

        parent = radio_button.find_element_by_xpath("./..")
        self._click_wait_for_clickable(parent)
        search_submit = self._sd.find_element_by_class_name("searchBeanButton")
        logging.debug('Submitting new billing period')
        search_submit.click()

    def get_data_usage(self):
        data_usage = self._sd.find_element_by_id("summaryDataOutWrapper")
        usage_text = self._get_text_wait_to_populate(data_usage)
        return usage_text

    @staticmethod
    def _click_wait_for_clickable(element, timeout=30):
        for _ in range(timeout):
            try:
                element.click()
            except (selenium_exceptions.ElementClickInterceptedException, selenium_exceptions.WebDriverException):
                logging.debug('Cannot click on the elemenent yet, waiting 1s...')
                sleep(1)
            else:
                return
        logging.debug('Failed to click on the elemenent')
        raise Timeout("Element was not clickable for {} seconds".format(timeout))

    @staticmethod
    def _get_text_wait_to_populate(element, timeout=30):
        for _ in range(timeout):
            if element.text:
                return element.text
            sleep(1)
        raise Timeout('Text of the element was not populated for {} seconds'.format(timeout))


class Timeout(Exception):
    pass
