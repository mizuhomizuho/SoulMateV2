import subprocess
import pathlib
import time
import sys
from django import db

sys.path.append(f'{pathlib.Path(__file__).parent.resolve()}/../..')
sys.path.append(f'{pathlib.Path(__file__).parent.resolve()}/../../soul_mate')

from parser.base import Base
from app_main.models import Pipe, Step2FreezingElements, Step3FreezingElements, Debug

class Step3(Base):

    __PULL: tuple[dict[str, str]] = (

        # {'proc': 'step3', 'el': 'chrome_3'},
        # {'proc': 'step3', 'el': 'chrome_my_vk'},
        # {'proc': 'step3', 'el': 'chrome_megafon_6114'},
        # {'proc': 'step3', 'el': 'chrome_mts_6192'},
        # {'proc': 'step3', 'el': 'chrome_mts_6227'},
        # {'proc': 'step3', 'el': 'chrome_mts_6209'},
        {'proc': 'step3', 'el': 'chrome_mts_6217'},
        # {'proc': 'step3', 'el': 'chrome_mts_6214'},

        {'proc': 'step2', 'el': 'ListVkCom'},
        {'proc': 'step2', 'el': 'ListVk24Com'},
        {'proc': 'step2', 'el': 'WennabeCom'},
        {'proc': 'step2', 'el': 'LibLiVkCom'},
        {'proc': 'step2', 'el': 'InfoPeopleCom'},
        {'proc': 'step2', 'el': 'VkstranaRu'},
        {'proc': 'step2', 'el': 'Top100vkCom'},
    )

    __process_pull: dict[str] = {}

    def init(self) -> None:

        Step2FreezingElements.objects.all().delete()
        Step3FreezingElements.objects.all().delete()
        Debug.objects.all().delete()

        while True:

            for item in self.__PULL:

                with open(f'{pathlib.Path(__file__).parent.resolve()}/exec.py', 'r') as f:
                    exec(f.read())
                if Base.stop:
                    print(f'Stop {__file__}')
                    return

                start_time = time.time()

                # db.connections.close_all()
                # for connection_name in db.connections.databases:
                #     db.connections[connection_name].close()

                pipe_ids: list[int] = []
                pipe_all = Pipe.objects.all().order_by('-pk')
                for pipe_el in pipe_all:
                    pipe_ids.append(pipe_el.pk)
                    print(pipe_el.value)
                Pipe.objects.filter(pk__in=pipe_ids).delete()

                proc_key: str = f'{item['proc']}_{item['el']}'

                if proc_key not in self.__process_pull:

                    args = (f'{pathlib.Path(__file__).parent.resolve()}/../../.venv/Scripts/python.exe',
                            f'{pathlib.Path(__file__).parent.resolve()}/{item['proc']}_process.py', item['el'])
                    self.__process_pull[proc_key] = {
                        'proc': subprocess.Popen(args),
                    }

                if time.time() - start_time < 1:
                    time.sleep(1 - (time.time() - start_time))

if __name__ == '__main__':

    Step3().init()