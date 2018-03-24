from django.urls import path
from . import views

app_name = 'panel'
urlpatterns = [
    path('',                    views.index,                    name='index'),
    path('login',               views.LoginView.as_view(),      name='login'),
    path('logout',              views.LogoutView.as_view(),     name='logout'),
    path('group/<normalSlug:slug>/approve/',  views.ApproveGroupView.as_view(),              name='group-approve'),
    path('group/<normalSlug:slug>/deny/',  views.DenyGroupView.as_view(),              name='group-deny'),
    path('group/<normalSlug:slug>/request-name-change/',  views.request_name_change, name='group-request-name-change'),
    path('group/edit/<normalSlug:slug>/',     views.placeholder,              name='group-edit'),
    path('group/delete/<normalSlug:slug>/',   views.placeholder,              name='group-delete'),
    path('teacher/add',         views.placeholder,              name='teacher-add'),
    path('teacher/edit/<normalSlug:slug>/',   views.placeholder,              name='teacher-edit'),
    path('teacher/delete/<normalSlug:slug>/', views.placeholder,              name='teacher-delete'),
]
