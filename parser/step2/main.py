import time
from io import StringIO
import sys
import pathlib
import subprocess
from datetime import datetime
import codecs

sys.path.append(f'{pathlib.Path().resolve()}/../..')
sys.path.append(f'{pathlib.Path().resolve()}/../../soul_mate')

from parser.base import Base
from list_vk_com import ListVkCom
from list_vk_24_com import ListVk24Com

class Step2(Base):

	last_starts: dict[str, float] = {}

	__class_pull: list = [ListVkCom, ListVk24Com,]

	def init(self):

		if len(sys.argv) >= 2 and sys.argv[1] == 'dev':
			self.__class_pull = [ListVk24Com,]

		while True:

			for s2_class in self.__class_pull:

				out = StringIO()
				sys.stdout = out

				is_error: bool = False
				try:
					s2_el = s2_class(self)
					s2_el.init()
				except Exception as ex:
					subprocess.Popen('py -c "import ctypes\nctypes.windll'
						 '.user32.MessageBoxW(0, \'Err\', \'Err\', 0x1000)"')
					self.__class_pull.remove(s2_class)
					is_error = True
					print('ERROR!!!')
					self._print_common_exception(ex)

				sys.stdout = sys.__stdout__
				if out.getvalue() != '':
					host_color = Base.color(f'{s2_el.HOST}:', 'OKCYAN')
					step_out: str = f'{host_color} {f'\n{host_color} '.join(out.getvalue().strip().split('\n'))}'
					print(step_out)
					if is_error:
						log_file: str = f'log/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{s2_class.__name__}'
						with codecs.open(log_file, 'w', 'utf-8') as f:
							f.write(step_out)

			# break
			time.sleep(1)

		# def sql_pretty():
		# 	import sqlparse
		# 	from django.db import connection
		# 	out = ''
		# 	for item in connection.queries:
		# 		out += ('\n\n' if out != '' else '') + sqlparse.format(item['sql'], reindent=True, keyword_case='upper')
		# 	return out
		#
		# print(sql_pretty())

if __name__ == '__main__':
	Step2().init()
