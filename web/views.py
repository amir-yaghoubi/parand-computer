from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from telegram_bot.telegrambot import get_group_link, pin_message as pin_message_telegram
from telegram_bot.errors import PermissionDenied
from .models import Group

from random import randint


def index(request):
    groups = Group.objects.order_by('-title').all()

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
    # Todo Query on models and find Group by slug
    group = get_object_or_404(Group, slug=slug)
    try:
        link = get_group_link(chat_id=group.chat_id)
        return redirect(link)
    except PermissionDenied as e:
        return render(request, 'web/index.html', {'link': '', 'title': e})


def pin_msg(request):
    pin_message_telegram(chat_id=-1001157994007, msg='امتحان پین توسط ربات')
    return HttpResponse('پیام ارسال شد')


def about(request):
    return render(request, 'web/index.html', {})