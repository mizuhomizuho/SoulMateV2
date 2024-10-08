import time
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
import sys
import pathlib

sys.path.append(f'{pathlib.Path().resolve()}/..')
sys.path.append(f'{pathlib.Path().resolve()}/../soul_mate')

class SoulMate:

    # url: str = 'https://vk.com/search/people?city_id=153&group_id=58944011&photo=1&sex=female'
    # link_type: str = 'search_people_in_group'
    # to_cat_id: int = 1

    url: str = 'https://vk.com/khabarovsk123'
    group_id: int = 81834858
    to_cat_id: int = 12
    link_type: str = 'in_group_v2'

    __chrome_user_data_dir: str = r'C:\Users\xxxx0\.chrome_3'
    __chrome_profile_directory: str = 'Default'

    driver: WebDriver
    stop_flag: bool = False

    def init(self) -> None:
        self.__init_driver()
        try:
            self.driver.maximize_window()
            self.driver.get(url=self.url)
            self.__main_interval()
        except Exception as ex:
            self.__print_common_exception(ex)
        finally:
            self.driver.close()
            self.driver.quit()

    def __print_common_exception(self, ex: Exception) -> None:
        print(f'{'{}'.format(traceback.extract_stack()[-2][2])} exception begin')
        print(ex)
        print(f'{'{}'.format(traceback.extract_stack()[-2][2])} exception end')

    def __main_interval(self) -> None:
        while True:
            try:
                with open('process.py', 'r') as f:
                    exec(f'def run(parent):\n\t{'\n\t'.join(f.read().split('\n'))}'
                         f'\n\tSoulMateProcess(parent)._init()\nrun(self)')
                    if self.stop_flag:
                        break
            except Exception as ex:
                self.__print_common_exception(ex)
            time.sleep(1)

    def __init_driver(self) -> None:
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        options.add_argument('--disable-extensions')
        # https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument(f'--user-data-dir={self.__chrome_user_data_dir}')
        options.add_argument(f'--profile-directory={self.__chrome_profile_directory}')
        self.driver = webdriver.Chrome(options=options)

if __name__ == '__main__':
    SoulMate().init()