import time
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
import sys
import pathlib
from selenium.webdriver.common.by import By
from selenium.common import NoSuchElementException
import subprocess
from datetime import datetime
import zipfile

sys.path.append(f'{pathlib.Path().resolve()}/../..')
sys.path.append(f'{pathlib.Path().resolve()}/../../soul_mate')

from cfg import CFG
from parser.base import Base
from app_catalog.models import Elements

class Step3(Base):

    __chrome_user_data_dir_prefix: str = r'C:\Users\xxxx0\.'
    __chrome_profile_directory: str = 'Default'

    __pull: dict[str, dict] = {}
    __chrome_pull: tuple[str] = ('chrome_3', 'my_vk')

    __STEP3_CAT_ID: int = 49
    __GOOD_CAT_ID: int = 50
    __LOCK_CAT_ID: int = 51
    __FROM_CAT_ID: int = 13

    __cur_item: Elements
    __cur_chrome: str

    def init(self) -> None:

        while True:
            for pull_key in self.__chrome_pull:
                try:

                    self.__cur_chrome = pull_key

                    if pull_key not in self.__pull:
                        self.__pull[pull_key] = {}
                        self.__pull[pull_key]['drv'] = self.__get_drv(pull_key)

                    time_diff: float = 0
                    time_now: float = time.time()
                    if 'last_start' in self.__pull[pull_key]:
                        time_diff = time_now - self.__pull[pull_key]['last_start']
                    if time_diff and time_diff < 8.88:
                        continue
                    self.__pull[pull_key]['last_start'] = time_now

                    self.__set_item()
                    url: str = f'https://vk.com/{self.__cur_item.nick}'
                    url = 'https://www.showmyip.com/'
                    print(Base.color(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'UNDERLINE'),
                        Base.color(pull_key, 'OKCYAN'),
                        Base.color(url, 'OKGREEN'))
                    self.__pull[pull_key]['drv'].get(url)
                    # self.__parse(pull_key)

                except Exception as ex:
                    self._print_common_exception(ex)
                    subprocess.Popen('py -c "import ctypes\nctypes.windll'
						 '.user32.MessageBoxW(0, \'Step3 err!\', \'Step3 err!\', 0x1000)"')
                    break

            time.sleep(10)

    def __set_item(self) -> Elements:

        self.__cur_item = Elements.objects.exclude(
            sections__in=(self.__GOOD_CAT_ID, self.__LOCK_CAT_ID)
        ).filter(sections=self.__FROM_CAT_ID).all()[0]

    def __parse(self, pull_key) -> None:

        is_no_lock = True
        try:
            self.__pull[pull_key]['drv'].find_element(
                By.CSS_SELECTOR, '#wall_tabs > ul > li > a > span.ui_tab_content_new')
        except NoSuchElementException:
            is_no_lock = False

        is_lock = True
        try:
            self.__pull[pull_key]['drv'].find_element(
                By.XPATH, "//h3[text()='Это закрытый профиль']")
        except NoSuchElementException:
            is_lock = False

        if is_no_lock and is_lock:
            raise Exception('Error type 1')

        if not is_no_lock and not is_lock:
            raise Exception('Error type 2')

        self.__set_res(is_lock)

    def __set_res(self, is_lock: bool):
        to_cat_id: int = self.__LOCK_CAT_ID if is_lock else self.__GOOD_CAT_ID
        self.__cur_item.sections.add(to_cat_id)
        if self.__GOOD_CAT_ID == to_cat_id:
            print(Base.color('GOOD!!!', 'WARNING'))
        else:
            print(Base.color('FAIL...', 'FAIL'))

    def __get_drv(self, pull_key) -> WebDriver:
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        if self.__cur_chrome in CFG['proxy']:
            self.__bild_proxy_ext()
            plugin_file = f'proxy_auth_plugin_{self.__cur_chrome}.zip'
            options.add_extension(plugin_file)
        else:
            options.add_argument('--disable-extensions')
        # https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument(f'--user-data-dir={self.__chrome_user_data_dir_prefix}{pull_key}')
        options.add_argument(f'--profile-directory={self.__chrome_profile_directory}')
        drv: WebDriver = webdriver.Chrome(options=options)
        drv.maximize_window()
        return drv

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

        plugin_file = f'proxy_auth_plugin_{self.__cur_chrome}.zip'

        with zipfile.ZipFile(plugin_file, 'w') as zp:
            zp.writestr('manifest.json', manifest_json)
            zp.writestr('background.js', background_js)

if __name__ == '__main__':
    Step3().init()