import time
from multiprocessing import Queue
import selenium
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium import webdriver
import sys
import zipfile
import datetime as dt
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.common import NoSuchElementException
import pathlib
import subprocess
import gc
import copy

from selenium.webdriver.remote.webelement import WebElement

sys.path.append(f'{pathlib.Path(__file__).parent.resolve()}/../..')
sys.path.append(f'{pathlib.Path(__file__).parent.resolve()}/../../soul_mate')

from cfg import CFG
from parser.base import Base
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

    def init(self, get_queue: Queue, res_queue: Queue, commit_queue: Queue) -> None:

        self._init_step(self.__cur_chrome, {
            'get_queue': get_queue,
            'res_queue': res_queue,
            'commit_queue': commit_queue,
        })

    def set_err(self) -> None:

        if not self.__is_err:
            subprocess.Popen(f'py -c "import ctypes'
                f'\nctypes.windll.user32.MessageBoxW(0, \'{self.__cur_chrome}\', \'Err step3\', 0x1000)"')
            try:
                self.__kill_drv()
            except AttributeError:
                pass

        self.__is_err = True

    def run(self) -> None:

        if self.__is_err:
            print(f'Isset err ({self.__cur_chrome})!')
            time.sleep(1)
            return

        try:
            self.__drv
        except AttributeError:
            self.__init_drv()

        # if len(sys.argv) >= 2 and sys.argv[1] == 'dev':
        #     exit()

        if not self.__set_item():
            print('No item!')
            return

        url: str = f'https://vk.com/{self.__cur_item.nick}'
        print(Base.color(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'UNDERLINE'),
            Base.color(self.__cur_item.pk, 'OKCYAN'),
            Base.color(url, 'OKGREEN'))

        try:
            self.__drv.get(url)
        except selenium.common.exceptions.TimeoutException:
            print('TimeoutException. Reload...')
            # self.__kill_drv()
            # self.__init_drv()
            self.__drv.get(url)

        try:
            self.__parse()
        except selenium.common.exceptions.TimeoutException as e:
            if str(e) != 'Message: timeout: Timed out receiving message from renderer: 300.000':
                self.__del_freez()
                raise
            print('TimeoutException (renderer). Reload...')
            self.__drv.get(url)
            self.__parse()

    def __print_err(self, el = None):

        if not el is None:
            print('textContent:', el.get_attribute('textContent'))
            print('innerHTML:', el.get_attribute('innerHTML'))
        print('HTML begin:')
        print(self.__drv.find_element(By.CSS_SELECTOR, 'html').get_attribute('innerHTML'))
        print('HTML end.')

    def __mktime(self, vk_date_el: WebElement) -> float:

        vk_date = vk_date_el.get_attribute('textContent')

        date_expl: list = vk_date.split(' ')
        if len(date_expl) == 4 and date_expl[2] == 'в':
            date_expl = [date_expl[0], date_expl[1], datetime.now().strftime('%Y')]
        if len(date_expl) == 5 and date_expl[3] == 'в':
            date_expl = [date_expl[0], date_expl[1], date_expl[2]]
        if len(date_expl) != 3:
            self.__del_freez()
            print('date_expl', date_expl)
            print('vk_date', vk_date)
            print('vk_date_el text:', vk_date_el.text)
            print('vk_date_el textContent:', vk_date_el.get_attribute('textContent'))
            print('vk_date_el innerHTML:', vk_date_el.get_attribute('innerHTML'))
            raise Exception('Err 1 !!!')
        mes_arr: dict = {
            'янв': '01', 'фев': '02', 'мар': '03', 'апр': '04', 'мая': '05', 'июн': '06',
            'июл': '07', 'авг': '08', 'сен': '09', 'окт': '10', 'ноя': '11', 'дек': '12',
        }

        try:
            return time.mktime(time.strptime(
                f'{date_expl[0]}/{mes_arr[date_expl[1]]}/{date_expl[2]}',
                '%d/%m/%Y'
            ))
        except Exception as e:
            print('Err 9:', date_expl, vk_date, e)
            raise

    def __s4_parse(self) -> None:

        while_i: int = 0
        while True:
            try:
                self.__drv.find_element(
                    By.CSS_SELECTOR, '#react_rootprofile .ProfileHeader .OwnerPageAvatar')
                break
            except NoSuchElementException:
                pass
            if while_i >= 10:
                print('Err 8 !!!')
                return
            while_i += 1
            time.sleep(1)

        try:
            last_seen_el = self.__drv.find_element(
                By.CSS_SELECTOR, '#react_rootprofile .ProfileIndicatorBadge__badgeLastSeen')
            last_seen_expl = last_seen_el.text.split(' ')
            if len(last_seen_expl) != 2:
                self.__del_freez()
                print('Len', len(last_seen_expl))
                raise Exception('Err 6 !!!')
            if last_seen_expl[1] == 'мес':
                last_seen_time = time.time() - 3600 * 24 * 31 * int(last_seen_expl[0])
            elif last_seen_expl[1] == 'н':
                last_seen_time = time.time() - 3600 * 24 * 7 * int(last_seen_expl[0])
            elif last_seen_expl[1] == 'дн':
                last_seen_time = time.time() - 3600 * 24 * int(last_seen_expl[0])
            elif last_seen_expl[1] == 'ч':
                last_seen_time = time.time() - 3600 * int(last_seen_expl[0])
            elif last_seen_expl[1] == 'мин':
                last_seen_time = time.time() - 60 * int(last_seen_expl[0])
            else:
                self.__del_freez()
                print(last_seen_expl)
                raise Exception('Err 7 !!!')
            self.__set_s4_res(last_seen_time)
            return
        except NoSuchElementException:
            pass

        last_post_time: float | None = None
        try:
            last_post_date_el = self.__drv.find_element(
                By.CSS_SELECTOR, '#page_wall_posts .PostHeaderSubtitle__item')
            last_post_time = self.__mktime(last_post_date_el)
        except NoSuchElementException:
            pass

        last_photo_el = None

        try:
            self.__drv.find_element(
                By.CSS_SELECTOR, '.vkuiTabs__in .vkuiTabsItem--selected[href^="/photos"]')
            last_photos_els = self.__drv.find_elements(
                By.CSS_SELECTOR, '.OwnerContentTabPhotos__items .OwnerContentTabPhotosItem[href^="/photo"]')
            if len(last_photos_els) > 6:
                self.__del_freez()
                print('Len', len(last_photos_els))
                raise Exception('Err 2 !!!')
            if len(last_photos_els):
                last_photo_el = last_photos_els[0]
        except NoSuchElementException:
            pass

        last_photo_time: float | None = None

        if not last_photo_el is None:
            last_photo_el.click()
            while_i: int = 0
            while True:
                try:
                    rel_date_el = self.__drv.find_element(
                        By.CSS_SELECTOR, '#pv_narrow_column_wrap #pv_date_info .rel_date')
                    last_photo_time = self.__mktime(rel_date_el)
                    break
                except NoSuchElementException:
                    pass
                if while_i >= 10:
                    raise Exception('Err 3 !!!')
                while_i += 1
                time.sleep(1)

        if last_photo_time is None:
            tab_btn_el: WebElement | None = None
            try:
                tab_btn_el = self.__drv.find_element(By.CSS_SELECTOR,
                '.vkuiTabs__in .vkuiTabsItem[href^="/photos"]:not(.vkuiTabsItem--selected)')
            except NoSuchElementException:
                pass
            if tab_btn_el is not None:
                tab_btn_el.click()
                break_2: bool = False
                while_i: int = 0
                while True:
                    try:
                        last_photo_el = self.__drv.find_element(
                            By.CSS_SELECTOR, '.OwnerContentTabPhotos__items .OwnerContentTabPhotosItem[href^="/photo"]')
                        last_photo_el.click()
                        while2_i: int = 0
                        while True:
                            try:
                                rel_date_el = self.__drv.find_element(
                                    By.CSS_SELECTOR, '#pv_narrow_column_wrap #pv_date_info .rel_date')
                                last_photo_time = self.__mktime(rel_date_el)
                                break_2 = True
                                break
                            except NoSuchElementException:
                                pass
                            if while2_i >= 10:
                                raise Exception('Err 5 !!!')
                            while2_i += 1
                            time.sleep(1)
                    except NoSuchElementException:
                        pass
                    if break_2:
                        break
                    if while_i >= 10:
                        print('Err 4 !!!')
                        break
                    while_i += 1
                    time.sleep(1)

        if last_post_time is None and last_photo_time is None:
            self.__set_s4_res(0)
            return

        if last_post_time is None:
            last_active_time = last_photo_time
        elif last_photo_time is None:
            last_active_time = last_post_time
        else:
            last_active_time = last_photo_time if last_photo_time > last_post_time else last_post_time

        self.__set_s4_res(last_active_time)

    def __del_freez(self) -> None:

        inst = copy.copy(self)
        try:
            del inst.__drv
            gc.collect()
        except AttributeError:
            pass

        Base.cur_commit_queue.put({
            'method': 'commit_del_freez',
            'inst': inst,
            'args': tuple(),
        })

    def commit_del_freez(self) -> None:
        
        self.__del_freez_base()

    def __kill_drv(self) -> None:

        self.__drv.close()
        self.__drv.quit()
        del self.__drv
        gc.collect()

    def __parse(self) -> None:

        if self._IS_STEP4:
            self.__s4_parse()
            return

        is_no_lock: bool = True
        try:
            self.__drv.find_element(
                By.CSS_SELECTOR, '#wall_tabs > ul > li > a > span.ui_tab_content_new')
        except NoSuchElementException:
            is_no_lock = False

        is_lock: bool = True
        try:
            self.__drv.find_element(
                By.XPATH, "//h3[text()='Это закрытый профиль']")
        except NoSuchElementException:
            is_lock = False

        if is_no_lock and is_lock:
            print('HTML begin:')
            print(self.__drv.find_element(By.CSS_SELECTOR, 'html').get_attribute('innerHTML'))
            print('HTML end.')
            self.__del_freez()
            raise Exception('Error type 1')

        if not is_no_lock and not is_lock:

            if self.__drv.title == 'Такой страницы нет':
                print('404...')
                self.__set_res(True)
                return

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
                pass

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
                pass

            try:
                text = 'Не удается получить доступ к сайту'
                self.__drv.find_element(
                    By.XPATH, f"//span[text()='{text}']")
                text = 'Превышено время ожидания ответа от сайта'
                self.__drv.find_element(
                    By.XPATH, f"//p[starts-with(text(),'{text}')]")
                print('Chrome err...')
                self.__del_freez()
                return
            except NoSuchElementException:
                pass

            try:
                box = self.__drv.find_element(
                    By.CSS_SELECTOR, '#profile_redesigned .PlaceholderMessageBlock__in')
                box.find_element(
                    By.XPATH, f"//div[contains(text(),'Мы обнаружили на')]")
                box.find_element(
                    By.XPATH, f"//div[contains(text(),'подозрительную активность и')]")
                box.find_element(
                    By.XPATH, f"//div[contains(text(),'временно заморозили её, чтобы вырвать из')]")
                print('Blocked (v2)...')
                self.__set_res(True)
                return
            except NoSuchElementException:
                pass

            try:
                box = self.__drv.find_element(
                    By.CSS_SELECTOR, '#react_rootprofile.ProfileWrapper__root')
                box.find_element(
                    By.XPATH, f"//h2[contains(text(),'Заблокированный пользователь')]")
                box.find_element(
                    By.XPATH, f"//div[contains(text(),'Данный материал заблокирован на территории"
                        f" Российской Федерации на основании требования Генеральной прокуратуры"
                        f" Российской Федерации от')]")
                print('Blocked (v3)...')
                self.__set_res(True)
                return
            except NoSuchElementException:
                pass

            try:
                el = self.__drv.find_element(By.CSS_SELECTOR, '#react_rootprofile.ProfileWrapper__root')
                if el.get_attribute('innerHTML') != '':
                    print('textContent:', el.get_attribute('textContent'))
                    print('innerHTML:', el.get_attribute('innerHTML'))
                    print('HTML begin:')
                    print(self.__drv.find_element(By.CSS_SELECTOR, 'html').get_attribute('innerHTML'))
                    print('HTML end.')
                    self.__del_freez()
                    raise Exception('Error type 3.3')
                self.__del_freez()
                print('JS err...')
                return
            except NoSuchElementException:
                print('HTML begin:')
                print(self.__drv.find_element(By.CSS_SELECTOR, 'html').get_attribute('innerHTML'))
                print('HTML end.')
                self.__del_freez()
                raise Exception('Error type 2')

        self.__set_res(is_lock)

    def __del_freez_base(self):
        
        Step3FreezingElements.objects.filter(pk=self.__cur_item.pk).delete()

    def __set_s4_res(self, last_active: float):

        inst = copy.copy(self)
        try:
            del inst.__drv
            gc.collect()
        except AttributeError:
            pass

        Base.cur_commit_queue.put({
            'method': 'commit_set_s4_res',
            'inst': inst,
            'args': (last_active,),
            'cur_chrome': self.__cur_chrome,
        })

    def commit_set_s4_res(self, last_active: float):

        self.__cur_item.time_last_active = datetime.fromtimestamp(last_active, dt.UTC)
        self.__cur_item.save()
        self.__del_freez_base()
        print(Base.color('Last active:', 'WARNING'),
              datetime.fromtimestamp(last_active).strftime('%Y-%m-%d %H:%M:%S'))

    def __set_res(self, is_bad: bool):

        inst = copy.copy(self)
        try:
            del inst.__drv
            gc.collect()
        except AttributeError:
            pass

        Base.cur_commit_queue.put({
            'method': 'commit_set_res',
            'inst': inst,
            'args': (is_bad,),
            'cur_chrome': self.__cur_chrome,
        })

    def commit_set_res(self, is_bad: bool):

        to_cat_id: int = self.__BAD_CAT_ID if is_bad else self.__GOOD_CAT_ID
        self.__cur_item.sections.add(to_cat_id)
        self.__cur_item.step3_parsed = True
        self.__cur_item.save()
        self.__del_freez_base()
        if self.__GOOD_CAT_ID == to_cat_id:
            print(Base.color('GOOD!!!', 'WARNING'))
        else:
            print(Base.color('Bad...', 'FAIL'))

    def __set_item(self) -> bool:

        if self._IS_STEP4:
            self.__cur_item = self._get_item(
                self.__cur_chrome,
                Step3FreezingElements,
                tuple(),
                {
                    'step3_good': True,
                    'age': 26,
                    'time_last_active__isnull': True
                },
            )
        else:
            self.__cur_item = self._get_item(
                self.__cur_chrome,
                Step3FreezingElements,
                {'step3_parsed': True},
                {'step2_good': True},
            )

        if not self.__cur_item:
            return False

        return True

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

        while True:

            options = webdriver.ChromeOptions()

            options.add_argument('--headless')
            # https://github.com/ultrafunkamsterdam/undetected-chromedriver
            # https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument(f'--user-data-dir={self.__CHROME_USER_DATA_DIR_PREFIX}{self.__cur_chrome}')
            options.add_argument(f'--profile-directory={self.__CHROME_PROFILE_DIRECTORY}')

            if self.__cur_chrome in CFG['proxy']:
                self.__bild_proxy_ext()
                plugin_file = f'{pathlib.Path(__file__).parent.resolve()}/proxy_auth_plugin_{self.__cur_chrome}.zip'
                options.add_extension(plugin_file)

            params: dict = {'options': options}

            try:
                self.__drv = webdriver.Chrome(**params)
                self.__drv.maximize_window()
                return
            except selenium.common.exceptions.SessionNotCreatedException:
                print('SessionNotCreatedException')
                time.sleep(2)