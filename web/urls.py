from django.urls import path
from . import views

app_name = 'web'
urlpatterns = [
    path('', views.IndexPage.as_view(), name='index'),
    path('لیست-اساتید', views.TeacherListView.as_view(), name='teachers'),
    path('help', views.help_view, name='help'),
    path('about', views.about, name='about'),
]