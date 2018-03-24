from telegram import (InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup)
from django.db.models import Q
from web.models import PendingGroup, Group
import logging

logger = logging.getLogger(__name__)


def search_group_callback(bot, update):
    query = update.inline_query.query

    if len(query) < 2:
        return

    groups = Group.objects.filter(Q(title__icontains=query) | Q(teacher__name__icontains=query))[:5]
    results = []

    for group in groups:
        title = '{0} استاد {1}'.format(group.title, group.teacher.name)
        content = InputTextMessageContent('📌 گروه: {0}\n👤 استاد: {1}\n📎 لینک: {2}'
                                          .format(group.title, group.teacher.name, group.link))

        results.append(InlineQueryResultArticle(group.chat_id, title, input_message_content=content))

    update.inline_query.answer(results)


def check_group_name(bot, update):
    query = update.callback_query

    pending_group = PendingGroup.objects.get(chat_id=query.message.chat_id)
    logger.info('check group name for {}'.format(query.data))
    if pending_group is not None:
        pending_group.title = query.message.chat.title
        pending_group.save()
        logger.info('pending group id: <{0}> name changed to <{1}>'.format(pending_group.chat_id,
                                                                           query.message.chat.title))
        msg = "❇️ درخواست بررسی مجدد نام گروه شما ثبت گردید. ❇️"
        return bot.edit_message_text(text=msg, chat_id=query.message.chat_id, message_id=query.message.message_id)

    else:

        logger.warning('cannot find group by id: <{}>'.format(pending_group.chat_id))
        msg = "❌ گروه شما یافت نشد ❌"
        return bot.edit_message_text(text=msg, chat_id=query.message.chat_id, message_id=query.message.message_id)
