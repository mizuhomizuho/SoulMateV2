import sys
import pathlib
import time
import subprocess
from django import db
from django.db import transaction

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

        # start_time = time.time()
        #
        # for connection_name in db.connections.databases:
        #     db.connections[connection_name].close()
        #
        # with transaction.atomic():
        #     self._step(self.__run, self.__set_err, self.__cur_class)
        #
        # if time.time() - start_time < 3:
        #     time.sleep(time.time() - start_time)
        #
        # for connection_name in db.connections.databases:
        #     db.connections[connection_name].close()

        while True:

            start_time: float  = time.time()

            with open(f'{pathlib.Path(__file__).parent.resolve()}/exec.py', 'r') as f:
                exec(f.read())
            if Base.stop:
                print(f'Stop {self.__cur_class}')
                return

            db.connections.close_all()

            with transaction.atomic():

                self._step(self.__run, self.__set_err, self.__cur_class)

            db.connections.close_all()

            print(f'{self.__cur_class}: Diff time {round(time.time() - start_time, 2)}')

            if time.time() - start_time < 3:
                time.sleep(time.time() - start_time)

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