import sys
import pathlib
import time
import subprocess
from multiprocessing import Queue

sys.path.append(f'{pathlib.Path(__file__).parent.resolve()}/../..')
sys.path.append(f'{pathlib.Path(__file__).parent.resolve()}/../../soul_mate')

from parser.base import Base
from parser.step2.list_vk_com import ListVkCom
from parser.step2.list_vk_24_com import ListVk24Com
from parser.step2.wennabe_com import WennabeCom
from parser.step2.lib_li_vk_com import LibLiVkCom
from parser.step2.info_people_com import InfoPeopleCom
from parser.step2.vkstrana_ru import VkstranaRu
from parser.step2.top100vk_com import Top100vkCom

class Step2Process(Base):

    __cur_class: str

    __is_err: bool = False

    def __init__(self, class_name: str):

        self.__cur_class = class_name

    def init(self, get_queue: Queue, res_queue: Queue, commit_queue: Queue) -> None:

        self._init_step(self.__cur_class, {
            'get_queue': get_queue,
            'res_queue': res_queue,
            'commit_queue': commit_queue,
        })

    def set_err(self) -> None:

        if not self.__is_err:
            subprocess.Popen(f'py -c "import ctypes'
                f'\nctypes.windll.user32.MessageBoxW(0, \'{self.__cur_class}\', \'Err step2\', 0x1000)"')

        self.__is_err = True

    def run(self) -> None:

        if self.__is_err:
            print(f'Isset err ({self.__cur_class})!')
            time.sleep(1)
            return

        globals()[self.__cur_class]().init()
