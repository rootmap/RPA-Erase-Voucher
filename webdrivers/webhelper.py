import json

from selenium import webdriver
from utils.constants import Browser
import os


class WebHelper:
    browser = Browser()

    def __init__(self):
        with open("./env_config.json") as config_file:
            conf = json.load(config_file)

        self.conf = conf

    def _current_path(self):
        return os.path.dirname(os.path.abspath(__file__))

    def open_browser(self, browser_name=browser.CHROME):
        browser = self._find_driver(browser_name)
        return browser

    def _find_driver(self, browser_name):
        browser = None
        options = webdriver.ChromeOptions()
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--ignore-certificate-errors')
        if 'chrome' in browser_name:
            driver_path = self.conf['chrome_driver_path']
            browser = webdriver.Chrome(driver_path, chrome_options=options)
        elif 'mozilla' in browser_name:
            driver_path = "\drivers\geckodriver.exe"
            browser = webdriver.Firefox(self._current_path() + driver_path)
        elif 'internet explorer' in browser_name:
            driver_path = "\drivers\IEDriverServer.exe"
            browser = webdriver.Ie(self._current_path() + driver_path)
        else:
            driver_path = self.conf['chrome_driver_path']
            browser = webdriver.Chrome(driver_path, chrome_options=options)
        return browser
