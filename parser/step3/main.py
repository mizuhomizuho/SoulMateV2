import os
import subprocess
import time
from multiprocessing import Process, Queue
import pathlib
import sys
from django.db import transaction

sys.path.append(f'{pathlib.Path(__file__).parent.resolve()}/../..')
sys.path.append(f'{pathlib.Path(__file__).parent.resolve()}/../../soul_mate')

from cfg import CFG
from parser.base import Base
from parser.step3.step2_process import Step2Process
from parser.step3.step3_process import Step3Process
from app_main.models import Step2FreezingElements, Step3FreezingElements, Debug, Options


class Step3(Base):

    __PULL: dict[str, dict] = {

        # 'chrome_3': {'inst': Step3Process},
        # 'chrome_my_vk': {'inst': Step3Process},
        # 'chrome_megafon_6114': {'inst': Step3Process},
        # 'chrome_mts_6192': {'inst': Step3Process},
        # 'chrome_mts_6227': {'inst': Step3Process},
        # 'chrome_mts_6209': {'inst': Step3Process},
        # 'chrome_mts_6217': {'inst': Step3Process},
        'chrome_mts_6214': {'inst': Step3Process},

        'ListVkCom': {'inst': Step2Process},
        'ListVk24Com': {'inst': Step2Process},
        'WennabeCom': {'inst': Step2Process},
        'LibLiVkCom': {'inst': Step2Process},
        'InfoPeopleCom': {'inst': Step2Process},
        'VkstranaRu': {'inst': Step2Process},
        'Top100vkCom': {'inst': Step2Process},
    }

    __get_queue: Queue
    __res_queues: dict[str, Queue]
    __commit_queue: Queue

    def __init__(self):

        self.__get_queue = Queue()
        self.__res_queues: dict[str, Queue] = {}
        self.__commit_queue = Queue()

    def process_queue_daemon(self) -> None:

        while True:

            client = self.__get_queue.get()

            start_time: float = time.time()

            with transaction.atomic():

                self.__res_queues[client['process_code']].put(self._get_item_base(
                    client['process_code'],
                    client['freezing_model'],
                    client['exclude_params'],
                    client['filter_params'],
                ))

            time_diff = time.time() - start_time
            if time_diff > 2:
                print(Base.color('Sleep 15', 'HEADER'))
                time.sleep(15)
            # else:
            #     time.sleep(1)

    def commit_queue_daemon(self) -> None:

        while True:

            client = self.__commit_queue.get()

            with transaction.atomic():

                getattr(client['inst'], client['method'])(*client['args'])

                la_el: Options = Options.objects.get(code='last_action')
                la_el.value = time.time()
                la_el.save()

    def init(self) -> None:

        connection = subprocess.Popen(
            f'plink.exe -ssh root@{CFG['srv']['ip']} -L 3307:localhost:3306 -pw {CFG['srv']['pass']}',
            shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        Step2FreezingElements.objects.all().delete()
        Step3FreezingElements.objects.all().delete()
        Debug.objects.all().delete()

        for proc in self.__PULL:

            params = self.__PULL[proc]
            self.__res_queues[proc] = Queue()
            inst = params['inst'](proc)
            p = Process(target=inst.init, args=(
                self.__get_queue,
                self.__res_queues[proc],
                self.__commit_queue,
            ))
            p.daemon = True
            p.start()

        p = Process(target=self.process_queue_daemon)
        p.daemon = True
        p.start()

        p = Process(target=self.commit_queue_daemon)
        p.daemon = True
        p.start()

        while True:
            pass

if __name__ == '__main__':

    Step3().init()