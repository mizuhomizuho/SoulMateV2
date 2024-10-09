import time
from io import StringIO
import sys
import pathlib

sys.path.append(f'{pathlib.Path().resolve()}/../..')
sys.path.append(f'{pathlib.Path().resolve()}/../../soul_mate')

from parser.base import Base
from list_vk_com import ListVkCom

class Step2(Base):

	last_starts: dict[str, float] = {}

	def init(self):

		while True:

			s2_pull = (ListVkCom,)

			for s2_class in s2_pull:

				out = StringIO()
				sys.stdout = out

				try:
					s2_el = s2_class(self)
					s2_el.init()
				except Exception as ex:
					self._print_common_exception(ex)

				sys.stdout = sys.__stdout__
				if out.getvalue() != '':
					host_color = Base.color(f'{s2_el.HOST}:', 'OKCYAN')
					print(f'{host_color} {f'\n{host_color} '.join(out.getvalue().strip().split('\n'))}')

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
