import traceback
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soul_mate.settings')
# os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'
django.setup()

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