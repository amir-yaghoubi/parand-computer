from django.shortcuts import render, redirect, get_object_or_404
from telegram_bot.telegrambot import get_group_link
from .models import Group


def index(request):
    groups = Group.objects.filter(show=True).order_by('-title').all()

    azmayeshgah = []
    takhasosi = []
    other = []

    for gp in groups:
        info = {'title': gp.title, 'teacher': str(gp.teacher), 'members': gp.members, 'slug': gp.slug}
        if gp.category == 'A':
            azmayeshgah.append(info)
        elif gp.category == 'T':
            takhasosi.append(info)
        else:
            other.append(info)

    obj_dict = {
        'azmayeshgah': azmayeshgah,
        'takhasosi': takhasosi,
        'other': other
    }
    return render(request, 'web/index.html', {'groups': obj_dict})


def export_group_link(request, slug):
    # پیدا کردن گروه بر اساس اسلاگ و صفحه 404 در صورت عدم پیدا شدن
    group = get_object_or_404(Group, slug=slug)
    request.group = group
    # دریافت لینک گروه از تلگرام که ممکن است دچار Exception شود
    # که رسیدگی به این خطاها توسط Middleware نوشته شده انجام میگردد
    # رجوع شود به web.middleware.TelegramErrorMiddleware
    link = get_group_link(chat_id=group.chat_id)

    return redirect(link)


def about(request):
    return render(request, 'web/index.html', {})


def help_view(request):
    return render(request, 'web/index.html', {})