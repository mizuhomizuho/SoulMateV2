from datetime import datetime
from multiprocessing import Process, Queue
import pathlib
import time
import sys
from django.db import transaction
from django import db
import gc

sys.path.append(f'{pathlib.Path(__file__).parent.resolve()}/../..')
sys.path.append(f'{pathlib.Path(__file__).parent.resolve()}/../../soul_mate')

from parser.base import Base
from parser.step3.step2_process import Step2Process
from parser.step3.step3_process import Step3Process
from app_main.models import Step2FreezingElements, Step3FreezingElements, Debug

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
        # 'LibLiVkCom': {'inst': Step2Process},
        # 'InfoPeopleCom': {'inst': Step2Process},
        # 'VkstranaRu': {'inst': Step2Process},
        # 'Top100vkCom': {'inst': Step2Process},
    }

    __get_queue: Queue
    __res_queues: dict[str, Queue]
    __commit_queue: Queue

    __proc_pull: dict[str, dict]

    def __init__(self):

        self.__get_queue = Queue()
        self.__res_queues: dict[str, Queue] = {}
        self.__commit_queue = Queue()

        self.__proc_pull = {}

    def init_proc(self, proc: str) -> Process:

        params = self.__PULL[proc]
        self.__res_queues[proc] = Queue()
        inst = params['inst'](proc)
        proc = Process(target=inst.init, args=(
            self.__get_queue,
            self.__res_queues[proc],
            self.__commit_queue,
        ))
        proc.daemon = True
        proc.start()
        return proc

    def process_queue_daemon(self) -> None:

        while True:

            client = self.__get_queue.get()

            db.connections.close_all()
            with transaction.atomic():
                self.__res_queues[client['process_code']].put(self._get_item_base(
                    client['process_code'],
                    client['freezing_model'],
                    client['exclude_params'],
                    client['filter_params'],
                ))
            db.connections.close_all()
            del client
            gc.collect()

    def commit_queue_daemon(self) -> None:

        while True:

            client = self.__commit_queue.get()

            # db.connections.close_all()
            with transaction.atomic():
                getattr(client['inst'], client['method'])(*client['args'])
            # db.connections.close_all()
            del client
            gc.collect()


    def init(self) -> None:

        Step2FreezingElements.objects.all().delete()
        Step3FreezingElements.objects.all().delete()
        Debug.objects.all().delete()

        for proc in self.__PULL:

            # self.__proc_pull[f'pull_{proc}'] = {
            #     'proc': self.init_proc(proc),
            #     # 'method': self.__init_proc,
            #     # 'args': (proc,),
            # }

            params = self.__PULL[proc]
            self.__res_queues[proc] = Queue()
            inst = params['inst'](proc)
            proc = Process(target=inst.init, args=(
                self.__get_queue,
                self.__res_queues[proc],
                self.__commit_queue,
            ))
            proc.daemon = True
            proc.start()

        for i in range(1):
            proc = Process(target=self.process_queue_daemon)
            proc.daemon = True
            proc.start()

        for i in range(1):
            proc = Process(target=self.commit_queue_daemon)
            proc.daemon = True
            proc.start()

        while True:
            time.sleep(8)

if __name__ == '__main__':

    Step3().init()