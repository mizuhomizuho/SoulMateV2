import re
from typing import Optional
import requests
from bs4 import BeautifulSoup
from parser.step2.base import Step2Base

class ListVkCom(Step2Base):

	HOST: str = 'list-vk.com'

	CAT_ID: int = 10
	NO_CITY_CAT_ID: int = 14
	MAN_CAT_ID: int = 15
	CONTINUE_CAT_ID: int = 24

	def init(self) -> None:

		vk_id: int = self._get_vk_id(self)

		try:
			req = self._request(f'https://{self.HOST}/{vk_id}/')
		except requests.exceptions.Timeout:
			print('Timed out')
			self._del_freezing()
			return

		if req.status_code == 404:
			self._set_continue()
			return

		if req.status_code == 502:
			print('Bad gateway 502...')
			self._del_freezing()
			return

		if req.status_code == 500:
			print('Http status 500...')
			self._del_freezing()
			return

		if req.status_code == 524:
			print('The origin web server timed out responding to this request. 524...')
			self._del_freezing()
			return

		if req.status_code != 200:
			print('BODY BEGIN:')
			print(req.text)
			print('BODY END.')
			self._del_freezing()
			raise Exception('Bad status_code', req.status_code)

		html: str = req.text

		soup = BeautifulSoup(html, 'html.parser')
		h1_el = soup.select('#dle-content .fheader h1')
		if not (len(h1_el) == 1):
			self._del_freezing()
			raise Exception('Err!!!')

		h1_expl = h1_el[0].contents[0].split(',')

		if not (len(h1_expl) >= 3 and h1_expl[2].strip() == self._get_city()):
			self._set_no_city()
			return

		sex_title_el = soup.findAll('span', string='Пол:', attrs={'class': 'white'})
		if not (len(sex_title_el) == 1):
			self._del_freezing()
			raise Exception('Err!!!')

		sex_title_parent = sex_title_el[0].findParent('li')
		if not (sex_title_parent is not None):
			self._del_freezing()
			raise Exception('Err!!!')

		sex_val_el = sex_title_parent.findChild(
			'span', string=re.compile('(женский|мужской)'), attrs={'class': 'white'})
		if not (sex_val_el is not None):
			self._del_freezing()
			raise Exception('Err!!!')
		if sex_val_el.contents[0] != 'женский':
			self._set_men()
			return

		vk_name: str = h1_expl[0]
		if not (isinstance(vk_name, str) and len(vk_name)):
			self._del_freezing()
			raise Exception('Err!!!')

		vk_age: Optional[int] = None
		if len(h1_expl) >= 2:
			output = re.search(r'(\d+)', h1_expl[1])
			if output is not None:
				vk_age = int(output.groups()[0])

		self._set_good(vk_name, vk_age)