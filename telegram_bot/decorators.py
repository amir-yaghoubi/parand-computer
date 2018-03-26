from web.models import Group
from .utils import get_model_object


def required_verify(func):
    def wrap(bot, update):
        # پاسخ گویی تنها به سوپر گروه ها
        if update.message.chat.type != 'supergroup':
            return

        group = get_model_object(Group, update.message.chat_id)

        if group is None:
            error_msg = '⛔️گروه شما هنوز ثبت نشده است. ☹️'
            return bot.sendMessage(update.message.chat_id, error_msg)

        return func(bot, update, group)
    return wrap

