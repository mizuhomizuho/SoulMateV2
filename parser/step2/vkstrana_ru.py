from typing import Optional
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from parser.step2.base import Step2Base

class VkstranaRu(Step2Base):

	HOST: str = 'vkstrana.ru'

	CAT_ID: int = 41
	NO_CITY_CAT_ID: int = 42
	MAN_CAT_ID: int = 43
	CONTINUE_CAT_ID: int = 44

	def init(self) -> None:

		vk_id: int = self._get_vk_id(self)

		try:
			req = self._request(f'https://{self.HOST}/{vk_id}')
		except requests.exceptions.Timeout:
			print('Timed out')
			return
		except requests.exceptions.ConnectionError:
			print('ConnectionError')
			return

		if req.status_code == 404:
			self._set_continue()
			return

		if req.status_code == 502:
			print('Internal Server Error 502...')
			return

		if req.status_code == 504:
			print('Internal Server Error 504...')
			return

		if req.status_code != 200:
			print('BODY BEGIN:')
			print(req.text)
			print('BODY END.')
			raise Exception('Bad status_code', req.status_code)

		html: str = req.text

		soup = BeautifulSoup(html, 'html.parser')

		box = soup.select('#page_contents .content_user.blok_content .information_about_me')

		if len(box) != 1:
			print('status_code:', req.status_code)
			print('BODY BEGIN:')
			print(req.text)
			print('BODY END.')

		assert len(box) == 1

		def get_field_val(title: str, optional: bool = False) -> str:
			el = box[0].findAll('h4', string=title)
			if optional and not len(el):
				return ''
			assert len(el) == 1
			el_parent = el[0].findParent('div', attrs={'class': 'line_block'})
			assert el_parent is not None
			el_parent = el_parent.findParent('div', attrs={'class': 'information_about_me_block'})
			assert el_parent is not None
			el_val = el_parent.findChild('p')
			assert el_val is not None
			return el_val.contents[0].strip()

		vk_city: str = get_field_val('Родной город', True)

		if self._get_city() not in vk_city:
			self._set_no_city()
			return

		vk_sex: str = get_field_val('Пол')
		assert vk_sex in ('женский', 'мужской')

		if vk_sex != 'женский':
			self._set_men()
			return

		vk_name: str = f'{get_field_val('Имя')} {get_field_val('Фамилия')}'

		vk_age: Optional[int] = None
		age_val: str = get_field_val('Дата рождения', True)
		age_val_expl = age_val.split(' ')
		if len(age_val_expl) == 3:
			vk_age = int(datetime.now().strftime('%Y')) - int(age_val_expl[2])
		if vk_age is None:
			age_val: str = get_field_val('Полных лет', True)
			age_val_expl = age_val.split(' ')
			if len(age_val_expl) == 2:
				vk_age = int(age_val_expl[0])

		self._set_good(vk_name, vk_age)

