from telegram.ext import CommandHandler, CallbackQueryHandler, InlineQueryHandler
from django_telegrambot.apps import DjangoTelegramBot
from .callback import check_group_name, search_group_callback
from . import commands
import logging

# config logger
handler = logging.FileHandler("logs/telegram-bot.log", "w", encoding="UTF-8")
formatter = logging.Formatter(u'%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def main():
    logger.info("Loading handlers for telegram bot")

    dp = DjangoTelegramBot.dispatcher

    dp.add_handler(CommandHandler("start", commands.start))
    dp.add_handler(CommandHandler("help", commands.get_help))
    dp.add_handler(CommandHandler("register", commands.register))
    dp.add_handler(CallbackQueryHandler(check_group_name, pattern=r'^gp_verify:name$'))
    dp.add_handler(InlineQueryHandler(search_group_callback))
    dp.add_handler(CommandHandler('get_id', commands.get_id))

    # log all errors
    dp.add_error_handler(commands.error)
