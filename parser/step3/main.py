from datetime import datetime
from multiprocessing import Process, Queue
import pathlib
import time
import sys

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
        'LibLiVkCom': {'inst': Step2Process},
        'InfoPeopleCom': {'inst': Step2Process},
        'VkstranaRu': {'inst': Step2Process},
        'Top100vkCom': {'inst': Step2Process},
    }

    __get_queue: Queue
    __res_queues: dict[str, Queue]

    def __init__(self):

        self.__get_queue = Queue()
        self.__res_queues: dict[str, Queue] = {}

    def get_els_daemon(self) -> None:

        while True:

            client = self.__get_queue.get()
            self.__res_queues[client['process_code']].put(self._get_item_base(
                client['process_code'],
                client['freezing_model'],
                client['exclude_params'],
                client['filter_params'],
            ))

    def init(self) -> None:

        Step2FreezingElements.objects.all().delete()
        Step3FreezingElements.objects.all().delete()
        Debug.objects.all().delete()

        for proc in self.__PULL:

            params = self.__PULL[proc]
            self.__res_queues[proc] = Queue()
            inst = params['inst'](proc)
            proc = Process(target=inst.init, args=(self.__get_queue, self.__res_queues[proc]))
            proc.daemon = True
            proc.start()

        for i in range(3):
            proc = Process(target=self.get_els_daemon)
            proc.daemon = True
            proc.start()

        while True:
            time.sleep(8)

if __name__ == '__main__':

    Step3().init()