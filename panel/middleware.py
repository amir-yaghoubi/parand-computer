from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin
from telegram_bot.errors import (BotIsKickedOut, ChatNotFound,
                                 ChatIdMigrated, BotIsNotMemberOfChat,
                                 CannotInvokeInviteLink, CannotSendMessage, MyTelegramError)
import logging
logger = logging.getLogger(__name__)


class TelegramErrorMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        logger.warning('{} exception on {}'.format(exception.__class__.__name__, request.path))

        if isinstance(exception, CannotInvokeInviteLink):
            context = {'error': 'عدم وجود دسترسی  لازم برای دریافت لینک گروه',
                       'error_text': 'ادمین گروه درخواستی شما دسترسی به لینک گروه را از ربات ما گرفته است.'}
            return render(request, 'panel/error_page.html', context, status=403)

        if isinstance(exception, BotIsKickedOut):
            context = {'error': 'ربات ما از گروه درخواستی شما حذف شده است!',
                       'error_text': 'لطفا برای حذف گروه اقدام نمایید.'}
            return render(request, 'panel/error_page.html', context, status=403)

        if isinstance(exception, BotIsNotMemberOfChat):
            context = {'error': 'ربات ما دیگر عضوی از گروه درخواستی شما نیست!',
                       'error_text': 'لطفا برای حذف گروه اقدام نمایید.'}
            return render(request, 'panel/error_page.html', context, status=404)

        if isinstance(exception, ChatNotFound):
            context = {'error': 'گروه درخواستی شما یافت نشد.',
                       'error_text': 'احتمالا گروه حذف گردیده است، به همین بهتر است برای حذف گروه اقدام نمایید.'}
            return render(request, 'panel/error_page.html', context, status=404)

        if isinstance(exception, CannotSendMessage):
            context = {'error': 'عدم وجود دسترسی لازم برای ارسال پیام',
                       'error_text': 'ربات ما دسترسی مورد نیاز برای ارسال پیام درخواستی شما را ندارد.'}
            return render(request, 'panel/error_page.html', context, status=403)

        if isinstance(exception, ChatIdMigrated):
            err_txt = 'شناسه گروه درخواستی شما به {} تغییر یافته است،'\
                      ' جهت بروز کردن این شناسه اقدام فرمایید.'.format(exception.new_id)
            context = {'error': 'تغییر شناسه گروه',
                       'error_text': err_txt}
            return render(request, 'panel/error_page.html', context, status=404)

        if isinstance(exception, MyTelegramError):
            context = {'error': 'خطایی از طرف تلگرام پیش آمده است.',
                       'error_text': exception.message}
            return render(request, 'panel/error_page.html', context, status=403)
        
        # let other exceptions handle by other ExceptionMiddleware.
        return None
