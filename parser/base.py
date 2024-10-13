import time
import traceback
from typing import Union, Type
from io import StringIO
import sys
import pathlib
from datetime import datetime
import codecs
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soul_mate.settings')
# os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'
django.setup()

from app_catalog.models import Elements
from app_main.models import Step3FreezingElements, Step2FreezingElements, Pipe

class Base:

    def _print_common_exception(self, ex: Exception) -> None:

        print(f'({'{}'.format(traceback.extract_stack()[-2][2])}) Exception begin:')
        print(f'Exception: {ex}')
        print(traceback.format_exc())
        print(f'({'{}'.format(traceback.extract_stack()[-2][2])}) Exception end.')

    @staticmethod
    def color(string: str, key: str) -> str:
        colors = {
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

        out = StringIO()
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
            p = pathlib.Path(__file__).parent.resolve()
            common_log_file: str = f'{p}/log/common_{datetime.now().strftime('%Y-%m-%d')}.log'
            with codecs.open(common_log_file, 'a', 'utf-8') as f:
                f.write(step_out)
            if is_error:
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

            exclude_ids: list[int] = []
            freezing = freezing_model.objects.all()
            for item in freezing:
                if item.process_code == process_code:
                    return Elements.objects.get(pk=item.elements_id)
                exclude_ids.append(item.elements_id)

            item = Elements.objects.exclude(**exclude_params)

            if exclude_ids:
                item = item.exclude(pk__in=exclude_ids)

            item = item.filter(**filter_params).all()[0]

            try:

                freezing_model.objects.create(elements_id=item.pk, process_code=process_code)
                print('Freezing:', item.pk, process_code)
                return item

            except django.db.utils.IntegrityError as e:

                if str(e) != f'UNIQUE constraint failed: app_main_{freezing_model.__name__.lower()}.elements_id':
                    raise

            time.sleep(1)
