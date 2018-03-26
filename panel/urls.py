from django.urls import path
from . import views

app_name = 'panel'
urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', views.LogoutView.as_view(), name='logout'),

    path('group/<normalSlug:slug>/approve/', views.ApproveGroupView.as_view(), name='group-approve'),
    path('group/<normalSlug:slug>/deny/', views.DenyGroupView.as_view(), name='group-deny'),
    path('group/<normalSlug:slug>/update/', views.update_pending_group, name='group-update'),
    path('group/<normalSlug:slug>/request-name-change/', views.request_name_change, name='group-request-name-change'),

    path('group/<groupSlug:slug>/edit/', views.EditGroupView.as_view(), name='group-edit'),
    path('group/<groupSlug:slug>/toggle-active/', views.group_toggle_active, name='group-toggle-active'),
    path('group/<groupSlug:slug>/send-message/', views.placeholder, name='group-send-message'),
    path('group/<groupSlug:slug>/invoke-link/', views.group_invoke_link, name='group-invoke-link'),
    path('group/<groupSlug:slug>/delete/', views.DeleteGroupView.as_view(), name='group-delete'),

    path('teacher', views.TeacherListView.as_view(), name='teacher-list'),
    path('teacher/add', views.AddTeacherView.as_view(), name='teacher-add'),
    path('teacher/<int:pk>/edit', views.EditTeacherView.as_view(), name='teacher-edit'),
]
