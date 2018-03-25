from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.views.generic import FormView, RedirectView, CreateView, DeleteView
from django.views.decorators.http import require_POST
from django.shortcuts import HttpResponseRedirect, get_object_or_404, redirect
from telegram_bot.actions import send_group_status_notification, get_group_link
from web.models import PendingGroup, Group, Teacher
from .forms import ApproveGroupForm
from .mixins import LoginRequiredMixin
from datetime import datetime


def index(request):
    pending_groups = PendingGroup.objects.all()
    return render(request, 'panel/index.html', {'pending': pending_groups})


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
    template_name = 'panel/form.html'
    form_class = ApproveGroupForm
    success_url = reverse_lazy('panel:index')

    def get_initial(self):
        # دریافت گروه نام گروه در حال انتظار برای پر کردن فرم اولیه
        pending = get_object_or_404(PendingGroup, slug=self.kwargs['slug'])
        return {'title': pending.title}

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
def request_name_change(request, slug):
    pending_group = get_object_or_404(PendingGroup, slug=slug)

    send_group_status_notification(pending_group.chat_id, 50)

    return redirect('panel:index')


def placeholder(request):
    pass