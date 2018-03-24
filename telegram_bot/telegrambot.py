from telegram.ext import CommandHandler
from django_telegrambot.apps import DjangoTelegramBot
from . import commands
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(filename='logs/telegram-bot.log', level=logging.INFO)


def main():
    logger.info("Loading handlers for telegram bot")

    dp = DjangoTelegramBot.dispatcher

    dp.add_handler(CommandHandler("start", commands.start))
    dp.add_handler(CommandHandler("help", commands.get_help))
    dp.add_handler(CommandHandler("register", commands.register))
    dp.add_handler(CommandHandler('get_id', commands.get_id))

    # log all errors
    dp.add_error_handler(commands.error)
