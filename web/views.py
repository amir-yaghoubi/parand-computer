from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from telegram_bot.telegrambot import get_group_link, pin_message as pin_message_telegram
from telegram_bot.errors import (PermissionDenied, ChatNotFound, BotIsKickedOut)
from .models import Group


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
    group = get_object_or_404(Group, slug=slug)
    try:
        link = get_group_link(chat_id=group.chat_id)
        return redirect(link)

    except PermissionDenied:
        group.active = False
        group.save()
        context = {'error': 'عدم دسترسی به لینک گروه',
                   'error_text': 'ادمین گروه درخواستی شما دسترسی به لینک گروه را از ربات ما گرفته است، به همین خاطر گروه غیر فعال شد.'}
        return render(request, 'web/errorPage.html', context)

    except ChatNotFound:
        group.delete()
        context = {'error': 'گروه درخواستی شما یافت نشد.',
                   'error_text': 'احتمالا گروه حذف گردیده است، به هماین دلیل این گروه از لیست گروه‌های سایت ما خارج شد.'}
        return render(request, 'web/errorPage.html', context)

    except BotIsKickedOut:
        group.delete()
        context = {'error': 'ربات ما از گروه درخواستی شما حذف شده است!',
                   'error_text': 'به همین دلیل گروه از سایت حذف می‌شود. در صورتی که فکر میکنید اشتباهی رخ داده است با ادمین تماس بگیرید.'}
        return render(request, 'web/errorPage.html', context)


def pin_msg(request):
    pin_message_telegram(chat_id=-1001157994007, msg='امتحان پین توسط ربات')
    return HttpResponse('پیام ارسال شد')


def about(request):
    return render(request, 'web/index.html', {})


def help_view(request):
    return render(request, 'web/index.html', {})