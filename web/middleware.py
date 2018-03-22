from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin
from telegram_bot.errors import (BotIsKickedOut, ChatNotFound, PermissionDenied)
import logging
logger = logging.getLogger(__name__)


class TelegramErrorMiddleware(MiddlewareMixin):
    def _delete_group(self, request):
        """Gets a request and check if
        there is a group Model object in it or not
        then will delete that group from db and set it None in request"""
        if request.group is not None:
            logger.warning('group: {0} removed from db.'.format(str(request.group)))
            request.group.delete()
            request.group = None

    def process_exception(self, request, exception):
        if isinstance(exception, PermissionDenied):
            logger.warning('PermissionDenied exception happend on {0}'.format(request.path))
            context = {'error': 'عدم دسترسی به لینک گروه',
                       'error_text': 'ادمین گروه درخواستی شما دسترسی به لینک گروه را از ربات ما گرفته است.'}
            return render(request, 'web/errorPage.html', context, status=403)

        if isinstance(exception, BotIsKickedOut):
            logger.warning('''BotIsKickedOut exception happend on {0}
            we will try to remove this group from db.'''.format(request.path))
            self._delete_group(request)
            context = {'error': 'ربات ما از گروه درخواستی شما حذف شده است!',
                       'error_text': 'به همین دلیل گروه از سایت حذف می‌شود. در صورتی که فکر میکنید اشتباهی رخ داده است با ادمین تماس بگیرید.'}
            return render(request, 'web/errorPage.html', context, status=403)

        if isinstance(exception, ChatNotFound):
            logger.warning('''ChatNotFound exception happend on {0}
            we will try to remove this group from db.'''.format(request.path))
            self._delete_group(request)
            context = {'error': 'گروه درخواستی شما یافت نشد.',
                       'error_text': 'احتمالا گروه حذف گردیده است، به همین دلیل این گروه از لیست گروه‌های سایت ما خارج شد.'}
            return render(request, 'web/errorPage.html', context, status=404)

        # let other exceptions handle by other ExceptionMiddleware.
        return None
