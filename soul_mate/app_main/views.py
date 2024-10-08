from django.core.cache import cache
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render

class Views:

    @staticmethod
    def page_not_found(request, exception) -> None:
        return HttpResponseNotFound('Page not found.')

    @staticmethod
    def index(request) -> None:
        var_str = ''
        for key in request.headers:
            var_str += f"\n\t'{key}': '{request.headers[key]}',"
        return render(request, 'app_main/index.html', {
            'headers': '{%s\n}' % var_str,
        })

    @staticmethod
    def clear_cache(request) -> None:
        cache.clear()
        return HttpResponse('<script>window.history.back()</script>')