from django.urls import path, register_converter
from .views import index, about, export_group_link
from .path_convertor import UnicodeSlug

# register our slug (unicode slug)
register_converter(UnicodeSlug, 'uSlug')

urlpatterns = [
    path('', index, name='index'),
    path('link/<uSlug:slug>/', export_group_link, name='get_group_link'),
    path('about', about, name='about'),
]