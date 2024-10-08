import re
from typing import Optional
import requests
import codecs
from bs4 import BeautifulSoup
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soul_mate.settings')
django.setup()

from app_catalog.models import Elements

class Step2:

	__HOST: str = 'list-vk.com'
	__CITY: str = 'Москва'
	# __CITY: str = 'Хабаровск'

	__PARSED_CAT_ID: int = 9

	def init(self):

		db_item = Elements.objects.exclude(sections=self.__PARSED_CAT_ID).all()[0]

		# def sql_pretty():
		# 	import sqlparse
		# 	from django.db import connection
		# 	out = ''
		# 	for item in connection.queries:
		# 		out += ('\n\n' if out != '' else '') + sqlparse.format(item['sql'], reindent=True, keyword_case='upper')
		# 	return out
		#
		# print(sql_pretty())

		return

		host: str = self.__HOST

		headers = {
			'Content-Length': '',
			'Content-Type': 'text/plain',
			'Host': host,
			'Connection': 'keep-alive',
			'Cache-Control': 'max-age=0',
			'Sec-Ch-Ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
			'Sec-Ch-Ua-Mobile': '?0',
			'Sec-Ch-Ua-Platform': '"Windows"',
			'Dnt': '1',
			'Upgrade-Insecure-Requests': '1',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
			'Sec-Fetch-Site': 'none',
			'Sec-Fetch-Mode': 'navigate',
			'Sec-Fetch-User': '?1',
			'Sec-Fetch-Dest': 'document',
			'Accept-Encoding': 'gzip, deflate, br, zstd',
			'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8,en-US;q=0.7,nl;q=0.6',
			'Cookie': 'csrftoken=WX9AWbKbGyJR5q1aNQTuHVnACG81zkdM; sessionid=sh73pw3ihxxcu1nm5qq0iqoj5lnytq77',
		}

		# город
		# пол
		# имя
		# возрост

		vk_id: int = 346223029
		vk_id: int = 564598093

		# req = requests.get(f'https://{host}/{vk_id}/', headers)
		# with codecs.open(f'tmp/{vk_id}.html', 'w', 'utf-8') as f:
		#     f.write(req.text)

		html: str = ''
		with codecs.open(f'tmp/{vk_id}.html', 'r', 'utf-8') as f:
			html = f.read()

		soup = BeautifulSoup(html, 'html.parser')
		h1_el = soup.select('#dle-content .fheader h1')
		assert len(h1_el) == 1

		h1_expl = h1_el[0].contents[0].split(',')

		if not (len(h1_expl) >= 3 and h1_expl[2].strip() == self.__CITY):
			print('Continue (city)...')
			return

		sex_title_el = soup.findAll('span', string=re.compile('Пол:'), attrs={'class': 'white'})
		assert len(sex_title_el) == 1

		sex_title_parent = sex_title_el[0].findParent('li')
		assert sex_title_parent != None

		sec_val_el = sex_title_parent.findChild('span', string=re.compile('(женский|мужской)'), attrs={'class': 'white'})
		assert sec_val_el != None
		if sec_val_el.contents[0] != 'женский':
			print('Continue (sex)...')
			return

		vk_name: str = h1_expl[0]
		assert isinstance(vk_name, str) and len(vk_name)

		vk_age: Optional[str] = None
		if len(h1_expl) >= 2:
			output = re.search(r'(\d+)', h1_expl[1])
			if output is not None:
				vk_age = output.groups()[0]

if __name__ == '__main__':
	Step2().init()
