import io
import time
import traceback
from typing import Union, Type
import sys
import pathlib
from datetime import datetime
import codecs
import sqlparse
from django.db import connection
import json
import pymysql
from pymysql.converters import escape_string
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soul_mate.settings')
# os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'
django.setup()

from app_catalog.models import Elements
from app_main.models import Step3FreezingElements, Step2FreezingElements, Pipe, Debug


class Base:

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
        for item in connection.queries:
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

    def _step(self, try_fns: callable, ex_fns: callable, step_name: str) -> None:

        out = io.StringIO()
        sys.stdout = out

        is_error: bool = False
        try:
            try_fns()
        except Exception as ex:
            ex_fns()
            is_error = True
            print('ERROR!!!')
            self._print_common_exception(ex)

        sys.stdout = sys.__stdout__
        if out.getvalue() != '':
            step_name_color = self.color(f'{step_name}:', 'OKCYAN')
            step_out: str = f'{step_name_color} {f'\n{step_name_color} '.join(out.getvalue().strip().split('\n'))}'
            Pipe.objects.create(value=step_out)
            if is_error:
                p = pathlib.Path(__file__).parent.resolve()
                log_file: str = f'{p}/log/el_err_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{step_name}.log'
                with codecs.open(log_file, 'w', 'utf-8') as f:
                    f.write(step_out)

    def _get_item(self,
        freezing_model: Union[Type[Step2FreezingElements], Type[Step3FreezingElements]],
        process_code: str,
        exclude_params: dict,
        filter_params: dict,
    ) -> Elements:

        while True:

            # Base.debug('_get_item while start', process_code)
            # Base.debug('sql_pretty1', process_code, Base.sql_pretty())

            freezing = freezing_model.objects.filter(process_code=process_code)
            if freezing:
                return Elements.objects.get(pk=freezing[0].elements_id)

            # Base.debug('sql_pretty2', process_code, Base.sql_pretty())

            item = Elements.objects.exclude(**exclude_params).exclude(
                pk__in=freezing_model.objects.all()).filter(**filter_params).order_by('?').first()

            if not item:
                print('The end!!!')
                time.sleep(8)

            # Base.debug('sql_pretty3', process_code, Base.sql_pretty())

            # conn = pymysql.connect(
            #     host='localhost',
            #     user='soul_mate',
            #     password='soul_mate',
            #     database='soul_mate',
            #     cursorclass=pymysql.cursors.DictCursor,)
            # cursor = conn.cursor()
            # cursor.execute(f"{item.query} LIMIT 1")
            # Base.debug('---check item.query---', process_code, cursor.fetchall())
            # conn.commit()
            # conn.close()

            # Base.debug('sql_pretty5', process_code, Base.sql_pretty())
            #
            # Base.debug('Free id', process_code, item.pk)

            # conn = pymysql.connect(
            #     host='localhost',
            #     user='soul_mate',
            #     password='soul_mate',
            #     database='soul_mate',
            #     cursorclass=pymysql.cursors.DictCursor,)
            # cursor = conn.cursor()
            # cursor.execute(f"SELECT * FROM app_catalog_elements_sections WHERE elements_id = {item.pk}")
            # Base.debug('---check elements_sections---', process_code, item.pk, cursor.fetchall())
            # conn.commit()
            # conn.close()

            try:

                freezing_model.objects.create(elements_id=item.pk, process_code=process_code)
                # Base.debug('Freezing', process_code, item.pk)
                return item

            except django.db.utils.IntegrityError:

                pass

            # Base.debug('No freezing, sleep', process_code, item.pk)

        # time.sleep(1)