from telegram import (Bot, InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.error import (TelegramError, Unauthorized, BadRequest)
from .errors import (PermissionDenied, BotIsKickedOut, ChatNotFound)
from . import app_settings
import logging

logger = logging.getLogger(__name__)


def get_group_link(chat_id, bot=None):
    """Get chat invite link from telegram
    param:
        chat_id: group chat id (required)
    return:
        group link
    raises:
        BotIsKickedOut,
        ChatNotFound,
        Permission Denied"""

    if chat_id is None or not isinstance(chat_id, int):
        raise ValueError('chat_id is invalid.')

    if bot is None:
        bot = Bot(app_settings.BOT_TOKEN)

    try:
        logger.info('Getting chat invite link. chat_id'.format(chat_id))
        return bot.export_chat_invite_link(chat_id)

    except Unauthorized as un_auth:
        if un_auth.message == 'Forbidden: bot was kicked from the supergroup chat':
            raise BotIsKickedOut()
        else:
            raise

    except BadRequest as bad_req:
        if bad_req.message == 'Not enough rights to export chat invite link':
            raise PermissionDenied()
        if bad_req.message == 'Chat not found':
            raise ChatNotFound()
        raise


def pin_message(chat_id, msg):
    bot = Bot(app_settings.BOT_TOKEN)
    try:
        message = bot.sendMessage(chat_id, msg)
        bot.pinChatMessage(chat_id, message.message_id)
    except TelegramError as err:
        logger.warning(err)
        bot.sendMessage(chat_id=chat_id, text='دسترسی برای تغییر نام یافت نشد.')


def send_group_status_notification(chat_id, status_code):
    """
    Function that send group status changes updates
        status_code:
            100 -> group verified and added to website
            50 -> group name is not clear enough, request changing name
            -100 -> group request declined by admins
    :param chat_id: Int
    :param status_code: Int (100, 50,-100)
    :return: Void
    """
    if not isinstance(chat_id, int) or not isinstance(status_code, int):
        raise ValueError('params must be integer.')

    bot = Bot(app_settings.BOT_TOKEN)
    if status_code == 100:
        msg = '✅ گروه شما توسط ادمین تایید گردید. ✅'
        bot.sendMessage(chat_id, msg)
    if status_code == 50:
        msg = '💢 عدم برخورداری نام گروه از قوانین خواسته شده. 💢\n'\
                'گروه شما جهت تایید توسط ادمین نیاز به نامی گویا دارد.\n'\
                ' 1️⃣ نام گروه باید شامل نام درس باشد.\n'\
                ' 2️⃣ نام گروه باید شامل نام استاد باشد.\n'\
                '\nبعد از تغییر نام گروه و پیروی از فرمت خواسته شده از دکمه زیر استفاده کنید.\n'

        keyboard = [[InlineKeyboardButton('بررسی مجدد نام گروه', callback_data='gp_verify:name')]]
        keyboard_markup = InlineKeyboardMarkup(keyboard)

        bot.sendMessage(chat_id, msg, reply_markup=keyboard_markup)
    if status_code == -100:
        msg = '⛔️گروه شما توسط ادمین تایید نگردید. ⛔️'
        bot.sendMessage(chat_id, msg)

    return


def get_group_name(chat_id):
    bot = Bot(app_settings.BOT_TOKEN)

    group = bot.get_chat(chat_id)

    return group.title


def leave_group(chat_id):
    bot = Bot(app_settings.BOT_TOKEN)

    msg = '❌❌ گروه شما از سایت حذف گردید. ❌❌'

    bot.send_message(chat_id, msg)
    bot.leave_chat(chat_id)
