from django.urls import path
from . import views

view_inst = views.Views()

urlpatterns = [
    path('', view_inst.index, name='catalog'),
    path('set-s4res/<int:id>/<slug:act>/', view_inst.set_s4res, name='set_s4res'),
    path('<path:section_path>/<slug:section_code>/', view_inst.section, name='section'),
    path('<slug:section_code>/', view_inst.section, name='section'),
]