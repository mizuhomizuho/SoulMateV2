from typing import Optional, TYPE_CHECKING
import requests
from bs4 import BeautifulSoup
from base import Step2Base
from datetime import datetime

if TYPE_CHECKING:
	from parser.step2.main import Step2

class Top100vkCom(Step2Base):

	HOST: str = 'top100vk.com'

	CAT_ID: int = 45
	NO_CITY_CAT_ID: int = 46
	MAN_CAT_ID: int = 47
	CONTINUE_CAT_ID: int = 48

	parent: 'Step2'

	def __init__(self, parent: 'Step2'):
		self.parent = parent

	def init(self) -> None:

		vk_id: Optional[int] = self._get_vk_id(self)
		if not isinstance(vk_id, int):
			return

		try:
			req = self._request(f'https://{self.HOST}/{vk_id}/')
		except requests.exceptions.Timeout:
			print('Timed out')
			return

		if req.status_code == 404:
			self._set_continue()
			return

		if req.status_code != 200:
			print('BODY BEGIN:')
			print(req.text)
			print('BODY END.')
			raise Exception('Bad status_code', req.status_code)

		html: str = req.text

		soup = BeautifulSoup(html, 'html.parser')

		box = soup.select('.card #timeline')
		assert len(box) == 1

		def get_field_val(title: str, optional: bool = False) -> str:
			el = box[0].findAll('div', string=title, attrs={'class': 'group-field__label'})
			if optional and not len(el):
				return ''
			assert len(el) == 1
			el_parent = el[0].findParent('div', attrs={'class': ('group-field', '_loading', 'js-group-field')})
			assert el_parent is not None
			el_val = el_parent.findChild('div', attrs={'class': ('group-field__value',)})
			assert el_val is not None
			return el_val.contents[0].strip()

		vk_city: str = get_field_val('Город')

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
		age_val_expl = age_val.split('.')
		if len(age_val_expl) == 3:
			vk_age = int(datetime.now().strftime('%Y')) - int(age_val_expl[2])

		self._set_good(vk_name, vk_age)

