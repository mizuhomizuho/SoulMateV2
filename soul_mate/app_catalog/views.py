from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Sections, Elements

class Views:

    @staticmethod
    def index(request):
        return render(request, 'app_catalog/index.html', {
            'tree': Sections.tree.get()['tree']
        })

    @staticmethod
    def section(request, section_code, section_path=None):
        section_el = get_object_or_404(Sections, code=section_code)
        pager = Paginator(
            Elements.objects.filter(sections=section_el).prefetch_related('sections'), 8
        ).get_page(request.GET.get('page'))
        return render(request, 'app_catalog/section.html', context={
            'tree': Sections.tree.get()['tree'],
            'section': section_el,
            'pager': pager,
        })