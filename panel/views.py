from django.shortcuts import render
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import FormView, RedirectView, CreateView, DeleteView, UpdateView, ListView
from django.views.decorators.http import require_POST
from django.shortcuts import HttpResponseRedirect, get_object_or_404, redirect
from telegram_bot.actions import (send_group_status_notification, get_group_link, get_group_name, leave_group, send_message)
from web.models import PendingGroup, Group, Teacher
from .forms import ApproveGroupForm, SendMessageForm
from datetime import datetime


@login_required
def index(request):
    pending_groups = PendingGroup.objects.all()
    verified_groups = Group.objects.all()
    return render(request, 'panel/index.html',
                  {'pending': pending_groups, 'verified': verified_groups, 'active': 'groups'})


class LoginView(FormView):
    template_name = 'panel/login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('panel:index')

    def dispatch(self, request, *args, **kwargs):
        # redirect admin if he/she is already logged in
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.get_success_url())
        else:
            return super(LoginView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # login admin and redirect to panel
        login(self.request, form.get_user())
        return HttpResponseRedirect(self.success_url)


class LogoutView(RedirectView):
    # where to redirect after logout
    pattern_name = 'panel:login'

    def get(self, request, *args, **kwargs):
        logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)


class ApproveGroupView(LoginRequiredMixin, CreateView):
    template_name = 'panel/group_form.html'
    form_class = ApproveGroupForm
    success_url = reverse_lazy('panel:index')

    def get_initial(self):
        # دریافت گروه نام گروه در حال انتظار برای پر کردن فرم اولیه
        pending = get_object_or_404(PendingGroup, slug=self.kwargs['slug'])
        return {'title': pending.title}

    def get_context_data(self, **kwargs):
        context = {'page_title': 'تایید گروه در حال انتظار'}
        context.update(kwargs)
        return super(ApproveGroupView, self).get_context_data(**context)

    def form_valid(self, form):
        pending = get_object_or_404(PendingGroup, slug=self.kwargs['slug'])
        form.instance.chat_id = pending.chat_id
        form.instance.admin_id = pending.admin_id
        form.instance.admin_username = pending.admin_username

        # may produce exception
        form.instance.link = get_group_link(pending.chat_id)

        form.instance.created_date = datetime.now()
        pending.delete()

        try:  # TODO Better Exception Handling
            send_group_status_notification(form.instance.chat_id, 100)
        except Exception:
            pass

        return super(ApproveGroupView, self).form_valid(form)


class DenyGroupView(LoginRequiredMixin, DeleteView):
    model = PendingGroup
    success_url = reverse_lazy('panel:index')
    template_name = 'panel/pending_group_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        chat_id = self.object.chat_id

        try:
            send_group_status_notification(chat_id, -100)
        except Exception:
            pass

        self.object.delete()
        return HttpResponseRedirect(self.get_success_url())


@require_POST
@login_required
def request_name_change(request, slug):
    pending_group = get_object_or_404(PendingGroup, slug=slug)

    send_group_status_notification(pending_group.chat_id, 50)

    return redirect('panel:index')


@require_POST
@login_required
def update_pending_group(request, slug):
    pending_group = get_object_or_404(PendingGroup, slug=slug)

    new_name = get_group_name(pending_group.chat_id)
    pending_group.title = new_name
    pending_group.save()

    return redirect('panel:index')


class EditGroupView(LoginRequiredMixin, UpdateView):
    model = Group
    fields = ['title', 'teacher', 'category', 'active']
    template_name = 'panel/group_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('panel:index')

    def form_valid(self, form):
        # برای تولید ایجاد اسلاگ جدید بعد از ویرایش
        form.instance.slug = None
        return super(EditGroupView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = {'page_title': 'ویرایش گروه ثبت شده'}
        context.update(kwargs)
        return super(EditGroupView, self).get_context_data(**context)


@require_POST
@login_required
def group_toggle_active(request, slug):
    group = get_object_or_404(Group, slug=slug)
    group.active = not group.active
    group.save()

    return redirect('panel:index')


@require_POST
@login_required
def group_invoke_link(request, slug):
    group = get_object_or_404(Group, slug=slug)
    group.link = get_group_link(group.chat_id)
    group.save()

    return redirect('panel:index')


class DeleteGroupView(LoginRequiredMixin, DeleteView):
    model = Group
    template_name = 'panel/group_confirm_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('panel:index')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        chat_id = self.object.chat_id

        try:
            leave_group(chat_id)
        except Exception:
            pass

        self.object.delete()
        return HttpResponseRedirect(self.get_success_url())


class TeacherListView(LoginRequiredMixin, ListView):
    model = Teacher
    template_name = 'panel/teacher_list.html'
    context_object_name = 'teachers'


class AddTeacherView(LoginRequiredMixin, CreateView):
    model = Teacher
    fields = ['name', 'email']
    template_name = 'panel/teacher_form.html'
    success_url = reverse_lazy('panel:teacher-list')

    def get_context_data(self, **kwargs):
        context = {'page_title': 'ثبت استاد جدید'}
        context.update(kwargs)
        return super(AddTeacherView, self).get_context_data(**context)


class EditTeacherView(LoginRequiredMixin, UpdateView):
    model = Teacher
    template_name = 'panel/teacher_form.html'
    fields = ['name', 'email']
    success_url = reverse_lazy('panel:teacher-list')

    def get_context_data(self, **kwargs):
        context = {'page_title': 'ویرایش استاد'}
        context.update(kwargs)
        return super(EditTeacherView, self).get_context_data(**context)


class SendMessageView(LoginRequiredMixin, FormView):
    template_name = 'panel/send_message_form.html'
    form_class = SendMessageForm
    success_url = reverse_lazy('panel:index')
    group = None

    def get(self, request, *args, **kwargs):
        slug = kwargs['slug']
        self.group = get_object_or_404(Group, slug=slug)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        slug = kwargs['slug']
        self.group = get_object_or_404(Group, slug=slug)
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['title'] = self.group.title
        return kwargs

    def form_valid(self, form):
        msg = form.cleaned_data['text_message']
        send_message(self.group.chat_id, msg)
        return super().form_valid(form)
