from __future__ import annotations
import io
import time
import traceback
from multiprocessing import Queue
from typing import Union, Type
import sys
import pathlib
from datetime import datetime
import codecs
import sqlparse
from django import db
import json
import pymysql
from django.db import transaction
from pymysql.converters import escape_string
from typing import TYPE_CHECKING
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soul_mate.settings')
# os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'
django.setup()

from app_catalog.models import Elements
from app_main.models import Debug, Step2FreezingElements, Step3FreezingElements

if TYPE_CHECKING:
    from parser.step3.step2_process import Step2Process
    from parser.step3.step3_process import Step3Process

class Base:

    cur_get_queue: Queue
    cur_res_queue: Queue

    __DEBUG_FILE: str = f'{pathlib.Path(__file__).parent.resolve()}/log/debug.json'

    __returned_sql: list = []

    def _print_common_exception(self, ex: Exception) -> None:

        print(f'({'{}'.format(traceback.extract_stack()[-2][2])}) Exception begin:')
        print(f'Exception: {ex}')
        print(traceback.format_exc())
        print(f'({'{}'.format(traceback.extract_stack()[-2][2])}) Exception end.')

    @staticmethod
    def print_to_string(*args, **kwargs) -> str:

        output = io.StringIO()
        print(*args, file=output, **kwargs)
        contents = output.getvalue()
        output.close()
        return contents

    @classmethod
    def sql_pretty(cls) -> str:

        out = ''
        i: int = 0
        for item in db.connection.queries:
            if i not in cls.__returned_sql:
                cls.__returned_sql.append(i)
                out += ('\n\n' if out != '' else '') + sqlparse.format(
                    item['sql'], reindent=True, keyword_case='upper')
            i += 1
        return out

    @classmethod
    def debug(cls, *vals) -> None:

        conn = pymysql.connect(host='localhost',
            user='soul_mate',
            password='soul_mate',
            database='soul_mate',)
        cursor = conn.cursor()
        sql = (f"INSERT INTO app_main_debug (time, value) VALUES "
               f"({time.time()}, '{escape_string(cls.print_to_string(vals))}')")
        cursor.execute(sql)
        conn.commit()
        conn.close()

    @classmethod
    def convert_debug(cls) -> None:

        arr: dict[float, dict] = {}
        for el in Debug.objects.all():
            if el.time not in arr:
                arr[el.time] = {}
            arr[el.time][el.pk] = el.value
        res_sorted = dict(sorted(arr.items()))
        with codecs.open(cls.__DEBUG_FILE, 'w', 'utf-8') as f:
            f.write(json.dumps(res_sorted))

    @staticmethod
    def color(string: str, key: str) -> str:
        colors: dict[str, str] = {
            'HEADER': '\033[95m',
            'OKBLUE': '\033[94m',
            'OKCYAN': '\033[96m',
            'OKGREEN': '\033[92m',
            'WARNING': '\033[93m',
            'FAIL': '\033[91m',
            'ENDC': '\033[0m',
            'BOLD': '\033[1m',
            'UNDERLINE': '\033[4m',
        }
        return f'{colors[key]}{string}{colors['ENDC']}'

    def _step(self, proc_code: str, proc_inst: Union[Step2Process, Step3Process]) -> None:

        out = io.StringIO()
        sys.stdout = out

        is_error: bool = False
        try:
            with transaction.atomic():
                proc_inst.run()
        except Exception as ex:
            proc_inst.set_err()
            is_error = True
            print('ERROR!!!')
            self._print_common_exception(ex)

        sys.stdout = sys.__stdout__
        if out.getvalue() != '':
            step_name_color = self.color(f'{proc_code}:', 'OKCYAN')
            step_out: str = f'{step_name_color} {f'\n{step_name_color} '.join(out.getvalue().strip().split('\n'))}'
            print(step_out)
            if is_error:
                p = pathlib.Path(__file__).parent.resolve()
                d: str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                log_file: str = f'{p}/log/el_err_{d}_{proc_code}.log'
                with codecs.open(log_file, 'w', 'utf-8') as f:
                    f.write(step_out)

    def _get_item(self,
        process_code: str,
        freezing_model: Union[Type[Step2FreezingElements], Type[Step3FreezingElements]],
        exclude_params: dict,
        filter_params: dict,
    ) -> Union[bool, Elements]:

        Base.cur_get_queue.put({
            'process_code': process_code,
            'freezing_model': freezing_model,
            'exclude_params': exclude_params,
            'filter_params': filter_params,
        })

        return Base.cur_res_queue.get()

    def _get_item_base(self,
        process_code: str,
        freezing_model: Union[Type[Step2FreezingElements], Type[Step3FreezingElements]],
        exclude_params: dict,
        filter_params: dict,
    ) -> Union[bool, Elements]:

        item = Elements.objects

        if isinstance(exclude_params, tuple):
            for excl_el in exclude_params:
                item = item.exclude(**excl_el)
        else:
            item = item.exclude(**exclude_params)

        item = item.exclude(pk__in=freezing_model.objects.all()).filter(
            **filter_params).only('id').order_by('?').first()

        if not item:
            print(f'The end ({process_code})...')
            return False

        # freezing = freezing_model.objects.filter(elements_id=item.pk)
        # if freezing:
        #     print(f'Isset freezing (1) {process_code} {item.pk}...')
        #     return False

        try:

            freezing_model.objects.create(elements_id=item.pk, process_code=process_code)
            return Elements.objects.get(pk=item.pk)

        except django.db.utils.IntegrityError:

            print(f'Isset freezing {process_code} {item.pk}...')
            return False