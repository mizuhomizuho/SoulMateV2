from typing import Optional
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from parser.step2.base import Step2Base

class ListVk24Com(Step2Base):

	HOST: str = 'list-vk-24.com'

	CAT_ID: int = 25
	NO_CITY_CAT_ID: int = 26
	MAN_CAT_ID: int = 27
	CONTINUE_CAT_ID: int = 28

	def init(self) -> None:

		vk_id: int = self._get_vk_id(self)

		vk_nick: str = self._get_vk_nick()

		try:
			req = self._request(f'https://{self.HOST}/vk/{vk_nick}/')
		except requests.exceptions.Timeout:
			print('Timed out')
			self._del_freezing()
			return

		if req.status_code == 404:
			self._set_continue()
			return

		if req.status_code == 500:
			print('Http status 500...')
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

		def get_field_val(title: str, optional: bool = False) -> str:
			el = soup.findAll('div', string=title, attrs={'class': 'field'})
			if optional and not len(el):
				return ''
			if not (len(el) == 1):
				self._del_freezing()
				raise Exception('Err!!!')
			el_parent = el[0].findParent('div', attrs={'class': 'line_data'})
			if not (el_parent is not None):
				self._del_freezing()
				raise Exception('Err!!!')
			el_val = el_parent.findChild('div', attrs={'class': 'field_data'})
			if not (el_val is not None):
				self._del_freezing()
				raise Exception('Err!!!')
			return el_val.contents[0].strip()

		vk_city1: str = get_field_val('Место проживания:', True)
		vk_city2: str = get_field_val('Родной город:', True)

		if self._get_city() not in vk_city1 and self._get_city() not in vk_city2:
			self._set_no_city()
			return

		vk_sex: str = get_field_val('Пол:')
		if not (vk_sex in ('женский', 'мужской')):
			self._del_freezing()
			raise Exception('Err!!!')

		if vk_sex != 'женский':
			self._set_men()
			return

		vk_name: str = get_field_val('Полное имя:')

		vk_age: Optional[int] = None
		age_val: str = get_field_val('Дата рождения:', True)
		age_val_expl = age_val.split('.')
		if len(age_val_expl) == 3:
			vk_age = int(datetime.now().strftime('%Y')) - int(age_val_expl[2])

		self._set_good(vk_name, vk_age)

