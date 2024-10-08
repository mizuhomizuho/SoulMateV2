from django.urls import path
from . import views

urlpatterns = [
    path('', views.Views.index, name='catalog'),
    path('<path:section_path>/<slug:section_code>/', views.Views.section, name='section'),
    path('<slug:section_code>/', views.Views.section, name='section'),
]