from typing import Optional
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from parser.step2.base import Step2Base

class WennabeCom(Step2Base):

	HOST: str = 'wennabe.com'

	CAT_ID: int = 29
	NO_CITY_CAT_ID: int = 30
	MAN_CAT_ID: int = 31
	CONTINUE_CAT_ID: int = 32

	def init(self) -> None:

		vk_id: int = self._get_vk_id(self)

		try:
			req = self._request(f'https://{self.HOST}/{vk_id}/')
		except requests.exceptions.Timeout:
			print('Timed out')
			return

		if req.status_code == 404:
			self._set_continue()
			return

		if req.status_code == 502:
			print('Bad gateway 502...')
			return

		if req.status_code != 200:
			print('BODY BEGIN:')
			print(req.text)
			print('BODY END.')
			raise Exception('Bad status_code', req.status_code)

		html: str = req.text

		soup = BeautifulSoup(html, 'html.parser')

		def get_field_val(title: str, optional: bool = False) -> str:
			el = soup.findAll('span', string=title, attrs={'class': 'white'})
			if optional and not len(el):
				return ''
			assert len(el) == 1
			el_parent = el[0].findParent('li')
			assert el_parent is not None
			el_val = el_parent.findChild('span', attrs={'class': 'white', 'style': 'text-align: right;'})
			assert el_val is not None
			return el_val.contents[0].strip()

		vk_city: str = get_field_val('Страна:', True)

		if self._get_city() not in vk_city:
			self._set_no_city()
			return

		vk_sex: str = get_field_val('Пол:')
		assert vk_sex in ('женский', 'мужской')

		if vk_sex != 'женский':
			self._set_men()
			return

		h1_el = soup.select('#dle-content .fheader h1')
		assert len(h1_el) == 1
		vk_name: str = h1_el[0].contents[0].strip()

		vk_age: Optional[int] = None
		age_val: str = get_field_val('Дата рождения:', True)
		age_val_expl = age_val.split('.')
		if len(age_val_expl) == 3:
			vk_age = int(datetime.now().strftime('%Y')) - int(age_val_expl[2])

		self._set_good(vk_name, vk_age)

