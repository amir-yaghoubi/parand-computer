from django.urls import path, register_converter
from . import views
from .path_convertor import UnicodeSlug

# register our slug (unicode slug)
register_converter(UnicodeSlug, 'uSlug')

urlpatterns = [
    path('', views.index, name='index'),
    path('link/<uSlug:slug>/', views.export_group_link, name='get_group_link'),
    path('help/', views.help_view, 'help'),
    path('about', views.about, name='about'),
]