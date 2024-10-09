import time
import ctypes
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from parser.main import Step1
from app_catalog.models import Elements
from app_main.models import Options

class Step1Process:

    __parent: Step1

    def __init__(self, parent: Step1):
        self.__parent = parent

    def __end_signal(self) -> None:

        ctypes.windll.user32.MessageBoxW(0, 'End', 'End', 0)
        self.__parent.stop_flag = True

    def __check_loaded(self) -> bool:

        if self.__parent.link_type == 'search_people_in_group':
            selector = '#select-status'
        elif self.__parent.link_type in ['in_group', 'in_group_v2']:
            selector = 'a.module_header[onclick^="return page.showPageMembers(event,"]'

        if not hasattr(self.__parent, 'smp_page_no_loaded_i'):
            self.__parent.smp_page_no_loaded_i = 0
            self.__parent.smp_page_no_loaded_i2 = 0
        try:
            self.__parent.driver.find_element(By.CSS_SELECTOR, selector)
        except NoSuchElementException:
            if self.__parent.smp_page_no_loaded_i >= 44:
                if self.__parent.smp_page_no_loaded_i2 >= 2:
                    print('Need restart')
                else:
                    print('Refresh')
                    self.__parent.driver.refresh()
                    self.__parent.smp_page_no_loaded_i = 0
                    self.__parent.smp_page_no_loaded_i2 += 1
            else:
                print(f'Page no loaded ({self.__parent.smp_page_no_loaded_i2}-{self.__parent.smp_page_no_loaded_i})')
            self.__parent.smp_page_no_loaded_i += 1
            return False

        return True

    def __parse_from_group_v2(self, vk_els: dict[str, dict], items: list) -> None:

        time.sleep(5)
        # return

        offset_el = Options.objects.get(code='parse_from_group_v2_offset')

        res = self.__parent.driver.execute_async_script(r"""
            const done = arguments[0]
            const offset = %(offset)s
            const fetch_res = fetch("https://vk.com/al_page.php?act=box", {
              "headers": {
                "accept": "*/*",
                "accept-language": "ru-RU,ru;q=0.9",
                "content-type": "application/x-www-form-urlencoded",
                "priority": "u=1, i",
                "sec-ch-ua": "\"Chromium\";v=\"130\", \"Google Chrome\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "x-requested-with": "XMLHttpRequest"
              },
              "referrer": "%(group_url)s",
              "referrerPolicy": "strict-origin-when-cross-origin",
              "body": "act=box&al=1&al_ad=0&offset=%(offset)s&oid=-%(group_id)d&tab=members",
              "method": "POST",
              "mode": "cors",
              "credentials": "include"
            });
            fetch_res
                .then((response) => {
                    if (response.status !== 200) {
                        done({res: false, status: response.status})
                    }
                    return response
                })
                .then(response => response.arrayBuffer())
                .then(buffer => (new TextDecoder('windows-1251')).decode(buffer))
                .catch(error => {
                    console.log('soul_mate_err_begin', error, 'soul_mate_err_end')
                    done({res: false, error: error})
                })
                .then(json => {
                    const boxSel = 'body>[data-soul-mate=parseBox]'
                    let boxEl = document.querySelector(boxSel)
                    if (!boxEl) {
                        document.body.insertAdjacentHTML('afterbegin', '<div data-soul-mate=parseBox></div>')
                        boxEl = document.querySelector(boxSel)
                        boxEl.style.display = 'none'
                    }
                    const data = JSON.parse(json)
                    boxEl.innerHTML = data.payload[1][offset > 0 ? 0 : 1]
                    done({res: true, box: boxEl})
                })
            """ % {
                'group_url': self.__parent.url,
                'group_id': self.__parent.group_id,
                'offset': offset_el.value
            })

        if res['res']:
            self.__parse_from_group_base(vk_els, items, box=res['box'], selector='.fans_fan_row')
            offset_el.value = int(offset_el.value) + len(items)
            offset_el.save()
        else:
            print(res)

    def __parse_from_group_base(self, vk_els: dict[str, dict], items: list, **kwargs) -> None:

        js_get_image_hash = """
            var hash = 0, ele = arguments[0], xhr = new XMLHttpRequest();
            var src = ele.src || window.getComputedStyle(ele).backgroundImage;
            xhr.open('GET', src.match(/https?:[^\"')]+/)[0], false);
            xhr.send();
            for (var i = 0, buffer = xhr.response; i < buffer.length; i++)
                hash = (((hash << 5) - hash) + buffer.charCodeAt(i)) | 0;
            return hash.toString(16).toUpperCase();
            """

        if 'box' in kwargs:
            box = kwargs['box']
        else:
            box = self.__parent.driver

        if 'selector' in kwargs:
            sel = kwargs['selector']
        else:
            sel = '#fans_rowsmembers>.fans_fan_row:not([data-soul-mate=parsed])'

        els = box.find_elements(By.CSS_SELECTOR, sel)
        for item in els:
            vk_id = item.get_attribute('data-id')
            ava_el = item.find_element(By.CSS_SELECTOR, 'img.fans_fan_img')
            ava_hash = self.__parent.driver.execute_script(js_get_image_hash, ava_el)
            ava_src = ava_el.get_attribute('src')
            try:
                url_expl = item.find_element(By.CSS_SELECTOR,
                'a.fans_fan_ph').get_attribute('href').split('/')
            except NoSuchElementException:
                try: item.find_element(By.CSS_SELECTOR, 'div.fans_fan_ph')
                except NoSuchElementException: raise Exception('No div.fans_fan_ph!!!')
                else: continue
            nick_name = url_expl[len(url_expl)-1]
            fi = ' '.join(item.find_element(By.CSS_SELECTOR,
                'a.fans_fan_lnk').get_attribute('innerHTML').split('<br>'))

            if 'selector' not in kwargs:
                self.__parent.driver.execute_script("""
                        arguments[0].dataset.soulMate = 'parsed'
                    """, item)

            items.append(item)
            if ava_hash != '-76AED24E':
                vk_els[nick_name] = Elements(name=fi, nick=nick_name, ava=ava_src, vk_id=vk_id)

    def __parse_from_group(self, vk_els: dict[str, dict], items: list) -> None:

        if not hasattr(self.__parent, 'smp_group_win_opened'):
            try:
                el = self.__parent.driver.find_element(By.CSS_SELECTOR,
                   'a.module_header[onclick^="return page.showPageMembers(event,"]')
                el.click()
                time.sleep(5)
            except NoSuchElementException:
                pass

        self.__parse_from_group_base(vk_els, items)

        if items:
            self.__parent.smp_group_win_opened = True

        self.__parent.driver.execute_script("""
            const boxSel = '#fans_rowsmembers>[data-soul-mate=heightBox]'
            let boxEl = document.querySelector(boxSel)
            if (!boxEl) {
                document.querySelector('#fans_rowsmembers').insertAdjacentHTML(
                    'afterbegin', '<div data-soul-mate=heightBox></div>')
                boxEl = document.querySelector(boxSel)
            }
            let arrForDel = []
            document.querySelectorAll(
                '#fans_rowsmembers>.fans_fan_row[data-soul-mate=parsed]'
            ).forEach((item) => {
                arrForDel.push(item)
                if (arrForDel.length === 5) {
                    boxEl.style.height = boxEl.offsetHeight + item.offsetHeight + 'px'
                    arrForDel.forEach(el => el.remove())
                    arrForDel = []
                }
            })
        """)

    def __parse_from_search_people_in_group(self, vk_els: dict[str, dict], items: list) -> None:
        els = self.__parent.driver.find_elements(By.CSS_SELECTOR,
            '[data-testid="userrichcell"].UserRichCell'
            '-module__container--CyEom:not([data-soul-mate=parsed])')
        for item in els:
            items.append(item)
            ava_link = item.find_element(By.CSS_SELECTOR, 'a.vkuiImageBase')
            link_expl = ava_link.get_attribute('href').split('?')
            link_expl2 = link_expl[0].split('/')
            nick_name = link_expl2[len(link_expl2)-1]
            ava_src = ava_link.find_element(
                By.CSS_SELECTOR, 'img.vkuiImageBase__img').get_attribute('src')
            fi = item.find_element(By.CSS_SELECTOR, 'div[data-testid="userrichcell-name"]').text
            self.__parent.driver.execute_script(
                'arguments[0].dataset.soulMate = "parsed"', item)
            vk_els[nick_name] = Elements(name=fi, nick=nick_name, ava=ava_src)

    def _init(self) -> None:

        # self.__parent.stop_flag = True

        if not self.__check_loaded():
            return

        vk_els: dict = {}
        items: list = []

        if self.__parent.link_type == 'search_people_in_group':
            self.__parse_from_search_people_in_group(vk_els, items)
        elif self.__parent.link_type == 'in_group':
            self.__parse_from_group(vk_els, items)
        elif self.__parent.link_type == 'in_group_v2':
            self.__parse_from_group_v2(vk_els, items)

        nicks: list[str] = list(vk_els)

        if not hasattr(self.__parent, 'smp_check_isset_dict'):
            self.__parent.smp_check_isset_dict = {}
        isset_nicks: list[str] = []
        for nick in nicks:
            try: self.__parent.smp_check_isset_dict[nick]
            except KeyError: self.__parent.smp_check_isset_dict[nick] = True
            else: isset_nicks.append(nick)
        if isset_nicks:
            print(f'Nicks isset: {isset_nicks}')

        for el in Elements.objects.filter(nick__in=nicks):
            del vk_els[el.nick]

        if vk_els:
            new_els = Elements.objects.bulk_create(list(vk_els.values()))
            bulk_insert: list = []
            for el in new_els:
                bulk_insert.append(Elements.sections.through(
                    elements_id=el.pk, sections_id=self.__parent.to_cat_id))
            if bulk_insert:
                Elements.sections.through.objects.bulk_create(bulk_insert)

        vk_els_len = len(vk_els)
        items_len = len(items)

        if not hasattr(self.__parent, 'smp_common_items_count'):
            self.__parent.smp_common_items_count = 0
            self.__parent.smp_common_vk_els_count = 0
        self.__parent.smp_common_items_count += items_len
        self.__parent.smp_common_vk_els_count += vk_els_len

        time_diff: float = 0
        time_now: float = time.time()
        if hasattr(self.__parent, 'smp_last_step_time'):
            time_diff = time_now - self.__parent.smp_last_step_time
        self.__parent.smp_last_step_time = time_now

        print(
            self.__parent.smp_common_items_count,
            items_len,
            len(self.__parent.smp_check_isset_dict),
            vk_els_len,
            time_diff,
            Options.objects.get(code='parse_from_group_v2_offset').value
        )

        if items_len == 0:
            if not hasattr(self.__parent, 'smp_end_signal_i'):
                self.__parent.smp_end_signal_i = 0
            if self.__parent.smp_end_signal_i >= 44:
                print('End')
                self.__end_signal()
                self.__parent.smp_end_signal_i = 0
                print(self.__parent.smp_common_items_count,
                    self.__parent.smp_common_vk_els_count)
            self.__parent.smp_end_signal_i += 1
            time.sleep(3)
        else:
            self.__parent.smp_end_signal_i = 0

        if self.__parent.link_type == 'search_people_in_group':
            self.__parent.driver.execute_script('window.scrollBy(0, document.body.scrollHeight)')
        elif self.__parent.link_type == 'in_group':
            if hasattr(self.__parent, 'smp_group_win_opened'):
                self.__parent.driver.execute_script("""
                    const boxWrap = document.querySelector('#box_layer_wrap')
                    boxWrap.scrollBy(0, boxWrap.scrollHeight)
                """)
