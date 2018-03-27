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
from telegram_bot.errors import MyTelegramError, CannotInvokeInviteLink
from web.models import PendingGroup, Group, Teacher
from .forms import ApproveGroupForm, SendMessageForm
from datetime import datetime


@login_required
def index(request):
    # دریافت تمام گروه های تایید شده و تایید نشده
    pending_groups = PendingGroup.objects.all()
    verified_groups = Group.objects.all()

    return render(request, 'panel/index.html',
                  {'pending': pending_groups, 'verified': verified_groups, 'active': 'groups'})


class LoginView(FormView):
    template_name = 'panel/login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('panel:index')

    def dispatch(self, request, *args, **kwargs):
        # درصورتی که کاربر لاگین کرده بود از این به صفحه مدیریت هدایتش میکنیم
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.get_success_url())
        # در غیر این صورت باید لاگین صورت بگیره
        else:
            return super(LoginView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # اگه فرم ارسالی درست باشه سعی در لاگین کردن کاربر با اطلاعات داده شده میکنیم
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
        # اضافه کردن title برای صفحه
        context = {'page_title': 'تایید گروه در حال انتظار'}
        context.update(kwargs)
        return super(ApproveGroupView, self).get_context_data(**context)

    def form_valid(self, form):
        # گروه در حال انتظار مربوطه رو از تلگرام واکشی میکنیم
        pending = get_object_or_404(PendingGroup, slug=self.kwargs['slug'])

        try:
            # سعی میکنیم لینک گروه رو دریافت کنیم
            form.instance.link = get_group_link(pending.chat_id)
        # اگه مجوز برای دسترسی به لینک گروه رو نداشتیم
        except CannotInvokeInviteLink:
            #  ارور رو به فرم اضافه میکنیم و به مراحل مربوط به فرم‌های نامعتبر رو اجرا میکنیم
            form.add_error(None, 'دسترسی برای دریافت لینک گروه در اختیار بات نیست!')
            return super(ApproveGroupView, self).form_invalid(form)

        # اضافه کردن فیلدهای لازم به فرم با مقادیری که در گروه‌های در حال انتظار داشتیم
        form.instance.chat_id = pending.chat_id
        form.instance.admin_id = pending.admin_id
        form.instance.admin_username = pending.admin_username
        form.instance.created_date = datetime.now()

        # حذف گروه از گروه‌های در حال انتظار
        pending.delete()

        # ارسال پیام تایید گروه
        try:
            # ارسال کد ۱۰۰ به معنای ثبت موفقیت آمیز هست
            send_group_status_notification(form.instance.chat_id, status_code=100)
        # در نظر نگرفتن خطاهای ممکن (مثلا اجازه ارسال پیام نداشته باشیم)
        except MyTelegramError:
            pass

        return super(ApproveGroupView, self).form_valid(form)


class DenyGroupView(LoginRequiredMixin, DeleteView):
    model = PendingGroup
    success_url = reverse_lazy('panel:index')
    template_name = 'panel/pending_group_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        chat_id = self.object.chat_id

        # ارسال پیام عدم پذیرش گروه
        try:
            # ارسال کد -۱۰۰ به معنی عدم پذیرش است
            send_group_status_notification(chat_id, status_code=-100)
        # در نظر نگرفتن خطاهای ممکن (مثلا اجازه ارسال پیام نداشته باشیم)
        except MyTelegramError:
            pass

        # حذف گروه از لیست گروه‌های در حال انتظار
        self.object.delete()

        return HttpResponseRedirect(self.get_success_url())


@require_POST
@login_required
def request_name_change(request, slug):
    # دریافت گروه در حال انتظار
    pending_group = get_object_or_404(PendingGroup, slug=slug)

    # ارسال کد 50 به معنی ارسال پیام درخواست تغییر نام هست
    # توجه داشته باشید که ما ارورهای ممکن رو اینجا پردازش نکردیم
    # و کار رو برای middleware نوشته شده خودمان گذاشتیم تا صفحه مربوط به خطا رو نمایش بده
    send_group_status_notification(pending_group.chat_id, 50)

    return redirect('panel:index')


@require_POST
@login_required
def update_pending_group(request, slug):
    # دریافت گروه در حال انتظار
    pending_group = get_object_or_404(PendingGroup, slug=slug)

    # دریافت نام گروه از تلگرام
    # توجه داشته باشید که ما ارورهای ممکن از طرف تلگرام رو اینجا پردازش نکردیم
    # و کار رو برای middleware نوشته شده مربوطه واگذار کردیم
    new_name = get_group_name(pending_group.chat_id)

    # تغییر نام قبلی گروه به نام دریافتی جدید و ذخیره آن
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
        # برای ایجاد اسلاگ جدید بعد از ویرایش مقدار اسلاگ رو None قرار میدیم
        # تا دوباره اسلاگ مرتبط با نام گروه ایجاد گردد
        form.instance.slug = None
        return super(EditGroupView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        # اضافه کردن موضوع صفحه به کانتکس
        context = {'page_title': 'ویرایش گروه ثبت شده'}
        context.update(kwargs)
        return super(EditGroupView, self).get_context_data(**context)


@require_POST
@login_required
def group_toggle_active(request, slug):
    # دریافت گروه درخواستی
    group = get_object_or_404(Group, slug=slug)

    # مقدار مربوط به نمایش یا عدم نمایش گروه رو معکوس میکنیم و گروه رو ذخیره میکنیم
    group.active = not group.active
    group.save()

    return redirect('panel:index')


@require_POST
@login_required
def group_invoke_link(request, slug):
    # دریافت گروه بر اساس اسلاگ
    group = get_object_or_404(Group, slug=slug)

    # دریافت لینک گروه جدید از تلگرام و ذخیره آن
    # توجه داشته باشید که ارورهای ممکن از تلگرام رو ما اینجا پردازش نکردیم
    # و برای middleware گذاشتیم تا خطای مربوطه رو اونجا نمایش بدیم
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

        # تلاش برای خارج کردن ربات از گروه
        try:
            leave_group(chat_id)
        # نادید گرفتن خطاهای ممکن
        except MyTelegramError:
            pass

        # حذف گروه
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
        # اضافه کردن page title به کانتکس
        context = {'page_title': 'ثبت استاد جدید'}
        context.update(kwargs)
        return super(AddTeacherView, self).get_context_data(**context)


class EditTeacherView(LoginRequiredMixin, UpdateView):
    model = Teacher
    template_name = 'panel/teacher_form.html'
    fields = ['name', 'email']
    success_url = reverse_lazy('panel:teacher-list')

    def get_context_data(self, **kwargs):
        # اضافه کردن page title به کانتکس
        context = {'page_title': 'ویرایش استاد'}
        context.update(kwargs)
        return super(EditTeacherView, self).get_context_data(**context)


class SendMessageView(LoginRequiredMixin, FormView):
    template_name = 'panel/send_message_form.html'
    form_class = SendMessageForm
    success_url = reverse_lazy('panel:index')
    group = None

    def get(self, request, *args, **kwargs):
        # دریافت گروه درخواستی و یا ارور 404 در صورت عدم وجود گروه
        # و اضافه کردن گروه به کلاس
        slug = kwargs['slug']
        self.group = get_object_or_404(Group, slug=slug)

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # دریافت گروه درخواستی و یا ارور 404 در صورت عدم وجود گروه
        # و اضافه کردن گروه به کلاس
        slug = kwargs['slug']
        self.group = get_object_or_404(Group, slug=slug)

        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # اضافه کردن title برای نمایش نام گروه در صفحه
        kwargs['title'] = self.group.title
        return kwargs

    def form_valid(self, form):
        # دریافت پیام تایپ شده جهت ارسال
        msg = form.cleaned_data['text_message']

        # تلاش برای ارسال پیام در گروه
        # توجه داشته باشید که ارورهای ممکن از تلگرام رو ما اینجا پردازش نکردیم
        # و برای middleware گذاشتیم تا خطای مربوطه رو اونجا نمایش بدیم
        send_message(self.group.chat_id, msg)

        return super().form_valid(form)
