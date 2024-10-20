from typing import Optional
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from parser.step2.base import Step2Base

class Top100vkCom(Step2Base):

	HOST: str = 'top100vk.com'

	CAT_ID: int = 45
	NO_CITY_CAT_ID: int = 46
	MAN_CAT_ID: int = 47
	CONTINUE_CAT_ID: int = 48

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

		if req.status_code != 200:
			print('BODY BEGIN:')
			print(req.text)
			print('BODY END.')
			self._del_freezing()
			raise Exception('Bad status_code', req.status_code)

		html: str = req.text

		soup = BeautifulSoup(html, 'html.parser')

		box = soup.select('.card #timeline')

		if not len(box) and req.status_code == 200:
			h1_404 = soup.findAll('h1', string='404', attrs={'class': 'heading'})
			if len(h1_404) == 1:
				self._set_continue()
				return
			if req.url == f'https://{self.HOST}/':
				self._set_continue('Redirect to frontpage...')
				return

		if not (len(box) == 1):
			self._del_freezing()
			raise Exception('Err!!!')

		def get_field_val(title: str, optional: bool = False) -> str:
			el = box[0].findAll('div', string=title, attrs={'class': 'group-field__label'})
			if optional and not len(el):
				return ''
			if not (len(el) == 1):
				self._del_freezing()
				raise Exception('Err!!!')
			el_parent = el[0].findParent('div', attrs={'class': ('group-field', '_loading', 'js-group-field')})
			if not (el_parent is not None):
				self._del_freezing()
				raise Exception('Err!!!')
			el_val = el_parent.findChild('div', attrs={'class': ('group-field__value',)})
			if not (el_val is not None):
				self._del_freezing()
				raise Exception('Err!!!')
			return el_val.contents[0].strip()

		vk_city: str = get_field_val('Город')

		if self._get_city() not in vk_city:
			self._set_no_city()
			return

		vk_sex: str = get_field_val('Пол')
		if not (vk_sex in ('женский', 'мужской')):
				self._del_freezing()
				raise Exception('Err!!!')

		if vk_sex != 'женский':
			self._set_men()
			return

		vk_name: str = f'{get_field_val('Имя')} {get_field_val('Фамилия')}'

		vk_age: Optional[int] = None
		age_val: str = get_field_val('Дата рождения', True)
		age_val_expl = age_val.split('.')
		if len(age_val_expl) == 3:
			vk_age = int(datetime.now().strftime('%Y')) - int(age_val_expl[2])

		self._set_good(vk_name, vk_age)

