import codecs
import io
import os
import subprocess
import time
from multiprocessing import Process, Queue
import pathlib
import sys
import django
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

        'chrome_3': {'inst': Step3Process},
        # 'chrome_my_vk': {'inst': Step3Process},
        'chrome_megafon_6114': {'inst': Step3Process},
        'chrome_mts_6192': {'inst': Step3Process},
        'chrome_mts_6227': {'inst': Step3Process},
        'chrome_mts_6209': {'inst': Step3Process},
        'chrome_mts_6217': {'inst': Step3Process},
        'chrome_mts_6214': {'inst': Step3Process},

        # 'ListVkCom': {'inst': Step2Process},
        # 'ListVk24Com': {'inst': Step2Process},
        # 'WennabeCom': {'inst': Step2Process},
        # 'LibLiVkCom': {'inst': Step2Process},
        # 'InfoPeopleCom': {'inst': Step2Process},
        # 'VkstranaRu': {'inst': Step2Process},
        # 'Top100vkCom': {'inst': Step2Process},
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

            # start_time: float = time.time()

            try:
                with transaction.atomic():
                    self.__res_queues[client['process_code']].put(self._get_item_base(
                        client['process_code'],
                        client['freezing_model'],
                        client['exclude_params'],
                        client['filter_params'],
                    ))
            except django.db.utils.OperationalError as e:
                print(Base.color(e, 'OKBLUE'))

            # time_diff = time.time() - start_time
            # if time_diff > 2:
            #     print(Base.color('Sleep 15', 'HEADER'))
            #     time.sleep(15)

    def commit_queue_daemon(self) -> None:

        while True:

            client = self.__commit_queue.get()

            out = io.StringIO()
            sys.stdout = out

            try:
                with transaction.atomic():
                    getattr(client['inst'], client['method'])(*client['args'])
                    Options.objects.filter(code='last_action').update(value=time.time())
            except django.db.utils.OperationalError as e:
                print(Base.color(e, 'OKBLUE'))

            sys.stdout = sys.__stdout__
            if out.getvalue() != '':
                proc_code = client['inst'].__class__.__name__
                if 'cur_chrome' in client:
                    proc_code = client['cur_chrome']
                step_name_color = self.color(f'{proc_code}:', 'OKCYAN')
                step_out: str = f'{step_name_color} {f'\n{step_name_color} '.join(out.getvalue().strip().split('\n'))}'
                print(step_out)

    def __save_proc_id(self, pid: int) -> None:

        with codecs.open(self._S3_PROC_IDS_FILE, 'a', 'utf-8') as f:
            f.write(f'{pid},')

    def init(self) -> None:

        with codecs.open(self._S3_PROC_IDS_FILE, 'w', 'utf-8') as f:
            f.write('')

        plink_p = subprocess.Popen(
            f'plink.exe -ssh root@{CFG['srv']['ip']} -L 3308:localhost:3306 -pw {CFG['srv']['pass']}',
            shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        self.__save_proc_id(plink_p.pid)

        try:
            with transaction.atomic():
                Step2FreezingElements.objects.all().delete()
                Step3FreezingElements.objects.all().delete()
                Debug.objects.all().delete()
        except django.db.utils.OperationalError as e:
            print(Base.color(e, 'OKBLUE'))

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
            self.__save_proc_id(p.pid)

        p = Process(target=self.process_queue_daemon)
        p.daemon = True
        p.start()
        self.__save_proc_id(p.pid)

        p = Process(target=self.commit_queue_daemon)
        p.daemon = True
        p.start()
        self.__save_proc_id(p.pid)

        # self.__save_proc_id(os.getpid())

if __name__ == '__main__':

    Step3().init()

    while True:
        pass