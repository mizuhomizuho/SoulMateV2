import re
from typing import Optional, TYPE_CHECKING
import requests
from bs4 import BeautifulSoup
from base import Step2Base

if TYPE_CHECKING:
	from parser.step2.main import Step2

class ListVkCom(Step2Base):

	HOST: str = 'list-vk.com'

	CAT_ID: int = 10
	NO_CITY_CAT_ID: int = 14
	MAN_CAT_ID: int = 15
	CONTINUE_CAT_ID: int = 24

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

		if req.status_code == 502:
			print('Bad gateway 502...')
			return

		if req.status_code == 500:
			print('Http status 500...')
			return

		if req.status_code == 524:
			print('The origin web server timed out responding to this request. 524...')
			return

		if req.status_code != 200:
			print('BODY BEGIN:')
			print(req.text)
			print('BODY END.')
			raise Exception('Bad status_code', req.status_code)

		html: str = req.text

		soup = BeautifulSoup(html, 'html.parser')
		h1_el = soup.select('#dle-content .fheader h1')
		assert len(h1_el) == 1

		h1_expl = h1_el[0].contents[0].split(',')

		if not (len(h1_expl) >= 3 and h1_expl[2].strip() == self._get_city()):
			self._set_no_city()
			return

		sex_title_el = soup.findAll('span', string='Пол:', attrs={'class': 'white'})
		assert len(sex_title_el) == 1

		sex_title_parent = sex_title_el[0].findParent('li')
		assert sex_title_parent is not None

		sex_val_el = sex_title_parent.findChild(
			'span', string=re.compile('(женский|мужской)'), attrs={'class': 'white'})
		assert sex_val_el is not None
		if sex_val_el.contents[0] != 'женский':
			self._set_men()
			return

		vk_name: str = h1_expl[0]
		assert isinstance(vk_name, str) and len(vk_name)

		vk_age: Optional[int] = None
		if len(h1_expl) >= 2:
			output = re.search(r'(\d+)', h1_expl[1])
			if output is not None:
				vk_age = int(output.groups()[0])

		self._set_good(vk_name, vk_age)