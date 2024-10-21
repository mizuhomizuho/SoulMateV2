import pathlib
import subprocess
import sys
import time
from datetime import datetime

sys.path.append(f'{pathlib.Path(__file__).parent.resolve()}/../..')
sys.path.append(f'{pathlib.Path(__file__).parent.resolve()}/../../soul_mate')

import django
from parser.base import Base
from app_main.models import Options

class Run(Base):

    __STEP_TIME: int = 60 * 5

    __last_time: float

    def __run(self):

        self.__last_time = time.time()

        base = f'{pathlib.Path(__file__).parent.resolve()}/../..'
        cmd = (fr"cd {base} && .venv\Scripts\activate && py parser/step3/main.py")

        sub_p = subprocess.Popen(cmd, shell = True, stdin = subprocess.PIPE,
              stdout = subprocess.PIPE, stderr = subprocess.PIPE)

        time.sleep(self.__STEP_TIME)

        return sub_p

    def init(self) -> None:

        connection = self.__run()

        while True:

            print(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))

            try:
                la_el: Options = Options.objects.get(code='last_action')
                self.__last_time = float(la_el.value)
            except django.db.utils.OperationalError:
                pass

            if self.__last_time < time.time() - self.__STEP_TIME:
                print('Restart')
                connection.kill()
                connection = self.__run()

            time.sleep(2)

if __name__ == '__main__':

    Run().init()

    # while True:
    #     try:
    #         subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=20, shell=True)
    #     except subprocess.CalledProcessError as e:
    #         print('CalledProcessError', e.returncode, e)