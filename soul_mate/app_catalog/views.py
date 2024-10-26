import time
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
import json
from app_catalog.models import Sections, Elements

class Views:

    __CUR_AGE: int = 26

    __S4_RES_CAT_ID_26_YES: int = 53
    __S4_RES_CAT_ID_26_NO: int = 54
    __S4_RES_CAT_ID_26_MB: int = 55

    def index(self, request):

        return render(request, 'app_catalog/index.html', {
            'tree': Sections.tree.get()['tree']
        })

    def set_s4res(self, request, id: int, act: str):

        cat_id = getattr(self, f'_{type(self).__qualname__}__S4_RES_CAT_ID_{self.__CUR_AGE}_{act.upper()}')
        el = Elements.objects.get(pk=id)
        el.sections.add(cat_id)
        res_dict = {'res': True}
        return HttpResponse(json.dumps(res_dict))

    def section(self, request, section_code, section_path=None):

        section_el = get_object_or_404(Sections, code=section_code)

        pager = Paginator(
            Elements.objects.filter(sections=section_el).prefetch_related('sections'), 18
        ).get_page(request.GET.get('page'))

        return render(request, 'app_catalog/section.html', context={
            'section': section_el,
            'pager': pager,
        })

    def s4good(self, request):

        els = Elements.objects.filter(
            step3_good=True,
            time_last_active__gte=datetime.fromtimestamp(time.mktime(time.strptime(
            '1/10/2024', '%d/%m/%Y'))).strftime('%Y-%m-%d %H:%M:%S'),
            age=self.__CUR_AGE,
        )
        els = els.exclude(sections__id__in=(
            getattr(self, f'_{type(self).__qualname__}__S4_RES_CAT_ID_{self.__CUR_AGE}_YES'),
            getattr(self, f'_{type(self).__qualname__}__S4_RES_CAT_ID_{self.__CUR_AGE}_NO'),
            getattr(self, f'_{type(self).__qualname__}__S4_RES_CAT_ID_{self.__CUR_AGE}_MB'),
        ))

        pager = Paginator(
            els.prefetch_related('sections'), 18
        ).get_page(request.GET.get('page'))

        good_count: str = f'[{pager.paginator.count}]'

        return render(request, 'app_catalog/section.html', context={
            'pager': pager,
            'good_count': good_count
        })