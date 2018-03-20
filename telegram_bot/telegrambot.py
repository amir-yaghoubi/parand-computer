from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram import Bot
from telegram.error import (TelegramError, Unauthorized, BadRequest)
from django_telegrambot.apps import DjangoTelegramBot
from .errors import (PermissionDenied, BotIsKickedOut, ChatNotFound)
from . import commands, app_settings
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(filename='logs/telegram-bot.log', level=logging.INFO)


def get_group_link(chat_id):
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


def change_name(chat_id, new_name):
    bot = Bot(app_settings.BOT_TOKEN)
    try:
        bot.setChatTitle(chat_id, new_name)
    except TelegramError:
        bot.sendMessage(chat_id=chat_id, text='دسترسی برای تغییر نام یافت نشد.')


def pin_message(chat_id, msg):
    bot = Bot(app_settings.BOT_TOKEN)
    try:
        message = bot.sendMessage(chat_id, msg)
        bot.pinChatMessage(chat_id, message.message_id)
    except TelegramError as err:
        logger.warning(err)
        bot.sendMessage(chat_id=chat_id, text='دسترسی برای تغییر نام یافت نشد.')


def main():
    logger.info("Loading handlers for telegram bot")

    # Default dispatcher (this is related to the first bot in settings.DJANGO_TELEGRAMBOT['BOTS'])
    dp = DjangoTelegramBot.dispatcher

    dp.add_handler(CommandHandler("start", commands.start))
    dp.add_handler(CommandHandler("help", commands.get_help))
    dp.add_handler(CommandHandler("register", commands.register))
    dp.add_handler(CommandHandler('get_id', commands.get_id))

    # log all errors
    dp.add_error_handler(commands.error)
