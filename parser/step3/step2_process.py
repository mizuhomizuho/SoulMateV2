import sys
import pathlib
import time
import subprocess

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

    def __init__(self, cur_class: str):

        self.__cur_class = cur_class

    def init(self) -> None:

        while True:

            self._step(self.__run, self.__set_err, self.__cur_class)

            time.sleep(8.88)

    def __set_err(self) -> None:

        if not self.__is_err:
            subprocess.Popen(f'py -c "import ctypes'
                f'\nctypes.windll.user32.MessageBoxW(0, \'{self.__cur_class}\', \'Err step2\', 0x1000)"')

        self.__is_err = True

    def __run(self) -> None:

        if self.__is_err:
            print('Isset err!')
            return

        globals()[self.__cur_class]().init()

if __name__ == '__main__':

    Step2Process(sys.argv[1]).init()