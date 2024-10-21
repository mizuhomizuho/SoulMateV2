import codecs
import os
import pathlib
import sys
import time
from datetime import datetime

sys.path.append(f'{pathlib.Path(__file__).parent.resolve()}/../..')
sys.path.append(f'{pathlib.Path(__file__).parent.resolve()}/../../soul_mate')

import django
from parser.base import Base
from app_main.models import Options
from parser.step3.main import Step3

class Run(Base):

    __STEP_TIME: int = 60 * 5

    __last_time: float

    def __run(self) -> None:

        Step3().init()

    def __set_time(self) -> None:

        self.__last_time = time.time()

        try:
            Options.objects.filter(code='last_action').update(value=self.__last_time)
        except django.db.utils.OperationalError:
            pass

    def init(self) -> None:

        self.__run()

        self.__set_time()

        while True:

            print(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))

            try:
                la_el: Options = Options.objects.get(code='last_action')
                last_time = float(la_el.value)
                if last_time < self.__last_time:
                    Options.objects.filter(code='last_action').update(value=self.__last_time)
                else:
                    self.__last_time = last_time
            except django.db.utils.OperationalError:
                pass

            if self.__last_time < time.time() - self.__STEP_TIME:
                self.__set_time()
                print('Restart')
                with codecs.open(self._S3_PROC_IDS_FILE, 'r+', 'utf-8') as f:
                    for pid in f.read().split(','):
                        if pid != '':
                            os.system(f'Taskkill /F /PID {pid}')
                            print(f'Taskkill {pid}')
                    f.write('')
                # os.system('Taskkill /IM python.exe /F')
                # os.system('Taskkill /IM plink.exe /F')
                os.system('Taskkill /IM chromedriver.exe /F')
                print('Taskkill chromedriver')
                self.__run()

            time.sleep(2)

if __name__ == '__main__':

    Run().init()

    # while True:
    #     try:
    #         subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=20, shell=True)
    #     except subprocess.CalledProcessError as e:
    #         print('CalledProcessError', e.returncode, e)