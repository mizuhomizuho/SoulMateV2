from django.contrib import admin
from .models import Sections, Elements

@admin.register(Sections)
class SectionsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'code', 'parent', 'sort', 'desc')
    list_editable = ('parent', 'sort')
    list_display_links = ('pk', 'name',)
    save_on_top = True

@admin.register(Elements)
class ElementsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name',)
    list_display_links = ('pk', 'name',)
    save_on_top = True