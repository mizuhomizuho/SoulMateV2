import time

import selenium
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium import webdriver
import sys
from typing import Any
import zipfile
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.common import NoSuchElementException
import pathlib
import subprocess

sys.path.append(f'{pathlib.Path(__file__).parent.resolve()}/../..')
sys.path.append(f'{pathlib.Path(__file__).parent.resolve()}/../../soul_mate')

from parser.base import Base
from cfg import CFG
from app_catalog.models import Elements
from app_main.models import Step3FreezingElements

class Step3Process(Base):

    __CHROME_USER_DATA_DIR_PREFIX: str = r'C:\Users\xxxx0\.'
    __CHROME_PROFILE_DIRECTORY: str = 'Default'

    __GOOD_CAT_ID: int = 50
    __BAD_CAT_ID: int = 51
    __FROM_CAT_ID: int = 13

    __drv: WebDriver
    __cur_chrome: str
    __cur_item: Elements
    __is_err: bool = False

    def __init__(self, chrome: str):

        self.__cur_chrome = chrome

    def init(self) -> None:

        while True:

            self._step(self.__run, self.__set_err, self.__cur_chrome)

            time.sleep(8.88)

    def __set_err(self) -> None:

        if not self.__is_err:
            subprocess.Popen(f'py -c "import ctypes'
                f'\nctypes.windll.user32.MessageBoxW(0, \'{self.__cur_chrome}\', \'Err step3\', 0x1000)"')
            try:
                self.__kill_drv()
            except AttributeError:
                pass

        self.__is_err = True

    def __run(self) -> None:

        if self.__is_err:
            print('Isset err!')
            return

        try:
            self.__drv
        except AttributeError:
            self.__init_drv()

        self.__set_item()

        url: str = f'https://vk.com/{self.__cur_item.nick}'
        print(Base.color(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'UNDERLINE'),
            Base.color(self.__cur_item.pk, 'OKCYAN'),
            Base.color(url, 'OKGREEN'))

        try:
            self.__drv.get(url)
        except selenium.common.exceptions.TimeoutException:
            print('TimeoutException. Reboot...')
            self.__kill_drv()
            self.__init_drv()
            self.__drv.get(url)

        self.__parse()

    def __kill_drv(self) -> None:

        self.__drv.close()
        self.__drv.quit()
        del self.__drv

    def __parse(self) -> None:

        def get_no_lock_el():
            return self.__drv.find_element(
                By.CSS_SELECTOR, '#wall_tabs > ul > li > a > span.ui_tab_content_new')

        def get_lock_el():
            return self.__drv.find_element(
                By.XPATH, "//h3[text()='Это закрытый профиль']")

        no_lock_el: Any = 'no_lock_el'
        is_no_lock: bool = True
        try:
            no_lock_el = get_no_lock_el()
        except NoSuchElementException:
            is_no_lock = False

        lock_el: Any = 'lock_el'
        is_lock: bool = True
        try:
            lock_el = get_lock_el()
        except NoSuchElementException:
            is_lock = False

        def check_more() -> dict:

            print('no_lock_el:', no_lock_el)
            print('lock_el:', lock_el)

            no_lock_el2 = 'no_lock_el2'
            try:
                no_lock_el2 = get_no_lock_el()
            except NoSuchElementException:
                pass

            lock_el2 = 'lock_el2'
            try:
                lock_el2 = get_lock_el()
            except NoSuchElementException:
                pass

            print('no_lock_el2:', no_lock_el2)
            print('lock_el2:', lock_el2)

            time.sleep(2)

            no_lock_el3 = 'no_lock_el3'
            is_no_lock3: bool = True
            try:
                no_lock_el3 = get_no_lock_el()
            except NoSuchElementException:
                is_no_lock3 = False

            lock_el3 = 'lock_el3'
            is_lock3: bool = True
            try:
                lock_el3 = get_lock_el()
            except NoSuchElementException:
                is_lock3 = False

            print('no_lock_el3:', no_lock_el3)
            print('lock_el3:', lock_el3)

            return {'is_no_lock3': is_no_lock3, 'is_lock3': is_lock3}

        if is_no_lock and is_lock:
            check_more()
            raise Exception('Error type 1')

        if not is_no_lock and not is_lock:
            if self.__drv.title == 'Такой страницы нет':
                print('404...')
                self.__set_res(True)
                return
            else:
                try:
                    self.__drv.find_element(
                        By.CSS_SELECTOR, '.PlaceholderMessageBlock__in')
                    text = 'К сожалению, нам пришлось заблокировать страницу'
                    self.__drv.find_element(
                        By.XPATH, f"//div[starts-with(text(),'{text}')]")
                    print('Blocked...')
                    self.__set_res(True)
                    return
                except NoSuchElementException:
                    try:
                        self.__drv.find_element(
                            By.CSS_SELECTOR, '.PlaceholderMessageBlock__in')
                        text = 'Страница удалена её владельцем.'
                        self.__drv.find_element(
                            By.XPATH, f"//div[text()='{text}']")
                        print('Deleted...')
                        self.__set_res(True)
                        return
                    except NoSuchElementException:
                        check_more_res = check_more()
                        if not check_more_res['is_no_lock3'] and not check_more_res['is_lock3']:
                            # print('Reboot...')
                            # self.__kill_drv()
                            # self.__init_drv()
                            # subprocess.Popen(f'py -c "import ctypes'
                            #      f'\nctypes.windll.user32.MessageBoxW(0, \'!is_no_lock && !is_lock3\', \'Err\', 0x1000)"')
                            # return
                            print(self.__drv.find_element(By.CSS_SELECTOR, 'html').get_attribute('innerHTML'))
                            raise Exception('Error type 2.1')
                        else:
                            raise Exception('Error type 2')

        self.__set_res(is_lock)

    def __set_res(self, is_bad: bool):

        to_cat_id: int = self.__BAD_CAT_ID if is_bad else self.__GOOD_CAT_ID
        self.__cur_item.sections.add(to_cat_id)
        Step3FreezingElements.objects.filter(pk=self.__cur_item.pk).delete()
        if self.__GOOD_CAT_ID == to_cat_id:
            print(Base.color('GOOD!!!', 'WARNING'))
        else:
            print(Base.color('Bad...', 'FAIL'))

    def __set_item(self) -> None:

        self.__cur_item = self._get_item(
            Step3FreezingElements,
            self.__cur_chrome,
            {'sections__in': (self.__GOOD_CAT_ID, self.__BAD_CAT_ID)},
            {'sections': self.__FROM_CAT_ID},
        )

    def __bild_proxy_ext(self):

        manifest_json = """
            {
                "version": "1.0.0",
                "manifest_version": 2,
                "name": "Chrome Proxy",
                "permissions": [
                    "proxy",
                    "tabs",
                    "unlimitedStorage",
                    "storage",
                    "<all_urls>",
                    "webRequest",
                    "webRequestBlocking"
                ],
                "background": {
                    "scripts": ["background.js"]
                },
                "minimum_chrome_version":"22.0.0"
            }
            """

        background_js = """
            var config = {
                mode: "fixed_servers",
                rules: {
                    singleProxy: {
                        scheme: "http",
                        host: "%s",
                        port: parseInt(%s)
                    },
                    bypassList: ["localhost"]
                }
            };
            chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
            function callbackFn(details) {
                return {
                    authCredentials: {
                        username: "%s",
                        password: "%s"
                    }
                };
            }
            chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
            );
            """ % (
                CFG['proxy'][self.__cur_chrome]['host'],
                CFG['proxy'][self.__cur_chrome]['port'],
                CFG['proxy'][self.__cur_chrome]['user'],
                CFG['proxy'][self.__cur_chrome]['pass'],
            )

        plugin_file = f'{pathlib.Path(__file__).parent.resolve()}/proxy_auth_plugin_{self.__cur_chrome}.zip'

        with zipfile.ZipFile(plugin_file, 'w') as zp:
            zp.writestr('manifest.json', manifest_json)
            zp.writestr('background.js', background_js)

    def __init_drv(self) -> None:

        options = webdriver.ChromeOptions()

        options.add_argument('--headless')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument(f'--user-data-dir={self.__CHROME_USER_DATA_DIR_PREFIX}{self.__cur_chrome}')
        options.add_argument(f'--profile-directory={self.__CHROME_PROFILE_DIRECTORY}')

        if self.__cur_chrome in CFG['proxy']:
            self.__bild_proxy_ext()
            plugin_file = f'{pathlib.Path(__file__).parent.resolve()}/proxy_auth_plugin_{self.__cur_chrome}.zip'
            options.add_extension(plugin_file)

        params: dict = {'options': options}

        self.__drv = webdriver.Chrome(**params)

        # self.__drv.maximize_window()

if __name__ == '__main__':

    Step3Process(sys.argv[1]).init()