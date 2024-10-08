from django.contrib import admin
from app_main.models import Options

@admin.register(Options)
class OptionsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'code', 'value')
    list_display_links = ('code',)
    save_on_top = True
