import platform
import logging
from pathlib import Path
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from utils.config import exMode, headless, ipbPassId, ipbHash

class selectDriver():

    def __init__(self):
        self.__driverPath = Path('chromedriver')
        self.__timeoutLimit = 180

        if platform.system() == 'Windows':
            self.__path = self.__driverPath / 'chromedriver_win32'
        elif platform.system() == 'Darwin':
            self.__path = self.__driverPath / 'chromedriver_mac64'
        else:
            self.__path = self.__driverPath / 'chromedriver_linux64'
        
        options = self.__setOption()
        self.driver = self.__getBrowser(self.__path, options)
        
    def __getBrowser(self, path:str, options):
        driver = webdriver.Chrome(executable_path=path.absolute().as_posix(), options=options)
        # set timeout
        driver.set_page_load_timeout(self.__timeoutLimit)
        return driver

    def __setOption(self):
        options = webdriver.ChromeOptions()
        # avoid logging flush screen
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # set window size
        options.add_argument('--width=512')
        options.add_argument('--height=384')
        # avoid load image to speed up
        prefs = {"profile.managed_default_content_settings.images": 2,
                "profile.managed_default_content_settings.media_stream":2,
                "profile.managed_default_content_settings.popups":2,
                "profile.managed_default_content_settings.javascript":2,
                "profile.default_content_setting_values.notifications":2,
                "profile.managed_default_content_settings.geolocation":2}
        options.add_experimental_option('prefs', prefs)
        # in background
        if headless:
            options.add_argument('--headless')
        return options

    def getPageSource(self, pageUrl:str):
        htmlText = ''
        while htmlText == '':
            try:
                self.driver.get(pageUrl)
                htmlText = self.driver.page_source
            except TimeoutException:
                logging.warning('Encounter timeout for URL({}), try to retry.'.format(pageUrl))
                self.driver.execute_script('window.stop()')
        return htmlText

    def setCookie(self):
        
        if exMode:
            self.driver.delete_all_cookies()

        # skip ehentai warning and exhentai pass
        self.driver.add_cookie({'name': 'nw', 'value': '1'})
        if exMode:
            self.driver.add_cookie({'name': 'ipb_member_id', 'value': ipbPassId})
            self.driver.add_cookie({'name': 'ipb_pass_hash', 'value': ipbHash})

    def close(self):
        self.driver.close()