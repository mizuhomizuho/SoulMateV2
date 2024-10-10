from typing import Any, Optional
import time
from datetime import datetime
from app_catalog.models import Elements
from parser.base import Base

class Step2Base:

	# __CITY: str = 'Москва'
	__CITY: str = 'Хабаровск'

	__FROM_CAT_ID: int = 7
	__PARSED_CAT_ID: int = 9
	__GOOD_CAT_ID: int = 13

	__cur_item: Elements
	__pull_el: Any

	def _get_headers(self, host: Optional[str] = None) -> dict[str, str]:

		if host is None:
			host = self.__pull_el.HOST

		return {
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

	def _get_city(self) -> str:
		return self.__CITY

	def __get_parsed_throughs(self, no_parsed: bool = False) -> list:
		throughs = [
			Elements.sections.through(elements_id=self.__cur_item.pk, sections_id=self.__pull_el.CAT_ID),
		]
		if not no_parsed:
			throughs.append(
				Elements.sections.through(elements_id=self.__cur_item.pk, sections_id=self.__PARSED_CAT_ID)
			)
		return throughs

	def __set_res(self, sections_id: int, no_parsed: bool = False) -> None:
		Elements.sections.through.objects.bulk_create(self.__get_parsed_throughs(no_parsed) + [
			Elements.sections.through(elements_id=self.__cur_item.pk, sections_id=sections_id),
		])

	def _set_no_city(self) -> None:
		print('Continue (city)...')
		self.__set_res(self.__pull_el.NO_CITY_CAT_ID)

	def _set_men(self) -> None:
		print('Continue (sex)...')
		self.__set_res(self.__pull_el.MAN_CAT_ID)

	def _set_continue(self) -> None:
		print('Continue (404)...')
		self.__set_res(self.__pull_el.CONTINUE_CAT_ID, True)

	def _get_vk_nick(self) -> str:
		return self.__cur_item.nick

	def _set_good(self, vk_name: str, vk_age: Optional[int]) -> None:
		self.__set_res(self.__pull_el.__GOOD_CAT_ID)
		msg: str = 'GOOD!!!'
		need_save_item: bool = False
		if self.__cur_item.name != vk_name:
			self.__cur_item.name = vk_name
			need_save_item = True
		if isinstance(vk_age, int):
			self.__cur_item.age = vk_age
			need_save_item = True
			msg += f' AGE {vk_age} !!!'
		if need_save_item:
			self.__cur_item.save()
		print(Base.color(msg, 'OKGREEN'))

	def _get_vk_id(self, pull_el: Any) -> Optional[int]:

		time_diff: float = 0
		time_now: float = time.time()
		if pull_el.__class__.__name__ in pull_el.parent.last_starts:
			time_diff = time_now - pull_el.parent.last_starts[pull_el.__class__.__name__]
		if time_diff and time_diff < 8.88:
			return
		pull_el.parent.last_starts[pull_el.__class__.__name__] = time_now

		self.__pull_el = pull_el

		# # self.__cur_pk = 346223029
		# self.__cur_pk = 564598093
		# return self.__cur_pk

		db_item = Elements.objects.exclude(
			sections__in=(self.__PARSED_CAT_ID, pull_el.CONTINUE_CAT_ID)
		).filter(sections__parent=self.__FROM_CAT_ID).all()[0]

		self.__cur_item = db_item

		print(Base.color(db_item.vk_id, 'OKBLUE'),
			  Base.color(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'HEADER'))

		return db_item.vk_id