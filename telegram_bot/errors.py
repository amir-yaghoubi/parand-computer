from telegram.error import (TelegramError, Unauthorized, BadRequest, ChatMigrated)
import logging

# set logger
logger = logging.getLogger(__name__)


class MyTelegramError(Exception):
    pass


class BotIsKickedOut(MyTelegramError):
    pass


class BotIsNotMemberOfChat(MyTelegramError):
    pass


class ChatNotFound(MyTelegramError):
    pass


class CannotSendMessage(MyTelegramError):
    pass


class CannotInvokeInviteLink(MyTelegramError):
    pass


class ChatIdMigrated(MyTelegramError):
    def __init__(self, message, new_chat_id):
        self.new_chat_id = new_chat_id
        super.__init__(message)


def exception_raiser(func):
    def wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Unauthorized as u:
            if u.message == 'Forbidden: bot was kicked from the supergroup chat':
                logger.info('we identify this error and generate "BotIsKickedOut" Exception.')
                raise BotIsKickedOut(u.message)

            if u.message == 'Forbidden: bot is not a member of the supergroup chat':
                logger.info('we identify this error and generate "BotIsNotMemberOfChat" Exception.')
                raise BotIsNotMemberOfChat(u.message)

            logger.warning('we didn\'t know this message: {} | we raise it again'.format(u.message))
            raise u  # raise again unhandled exceptions

        except BadRequest as b:
            if b.message == 'Have no rights to send a message':
                logger.info('we identify this error and generate "CannotSendMessage" Exception.')
                raise CannotSendMessage(b.message)

            if b.message == 'Not enough rights to export chat invite link':
                logger.info('we identify this error and generate "CannotInvokeInviteLink" Exception.')
                raise CannotInvokeInviteLink(b.message)

            if b.message == 'Chat not found':
                logger.info('we identify this error and generate "ChatNotFound" Exception.')
                raise ChatNotFound(b.message)

            logger.warning('we didn\'t know this message: {} | we raise it again'.format(b.message))
            raise b  # raise again unhandled exceptions

        except ChatMigrated as c:
            logger.info(
                'chat_id is changed to "{}" ,we raise it again so views can change chat_id'.format(c.new_chat_id))
            raise ChatIdMigrated(c.message, c.new_chat_id)

        except TelegramError as t:
            raise t  # raise again unhandled exceptions

    return wrap


@exception_raiser
def error_handler_hook(bot, update, err):
    logger.warning('Update "%s" caused error "%s"', update, err)
    raise err
