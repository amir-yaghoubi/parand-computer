from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.views.generic import FormView, RedirectView, ListView
from django.shortcuts import HttpResponse, HttpResponseRedirect, get_object_or_404, redirect
from web.models import PendingGroup, Group, Teacher


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


def approve_group(request, slug):
    '''Place holder'''
    pending = get_object_or_404(PendingGroup, slug=slug)
    teacher = Teacher.objects.get(pk=1)
    Group.objects.create(title=pending.title,
                         chat_id=pending.chat_id, admin_id=pending.admin_id,
                         admin_username=pending.admin_username,
                         category='T', active=True, teacher=teacher)
    pending.delete()
    return redirect('panel:index')

def placeholder(request):
    pass