from web.models import PendingGroup
import logging

logger = logging.getLogger(__name__)


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
