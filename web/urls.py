from django.urls import path
from . import views

app_name = 'web'
urlpatterns = [
    path('', views.IndexPage.as_view(), name='index'),
    path('لیست-اساتید', views.TeacherListView.as_view(), name='teachers'),
    path('راهنما', views.help_view, name='help'),
    path('درباره-ما', views.about, name='about'),
]