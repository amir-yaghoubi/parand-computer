from telegram import (InlineQueryResultArticle, InputTextMessageContent)
from django.db.models import Q
from web.models import PendingGroup, Group
import logging

logger = logging.getLogger(__name__)


def search_group_callback(bot, update):
    query = update.inline_query.query

    # عدم پاسخ گویی به نوشته های زیر ۲ کاراکتر
    if len(query) < 2:
        return

    # دریافت گروه‌های که نام و یا نام استادشان شامل رشته ورودی کاربر باشد
    groups = Group.objects.filter(Q(title__icontains=query) | Q(teacher__name__icontains=query))[:5]
    results = []

    # ایجاد خروجی مطلوب تلگرام از گروه‌های یافت شده
    for group in groups:
        title = '📌  گروه {0} 👤  استاد {1}'.format(group.title, group.teacher.name)
        content = InputTextMessageContent('📌 گروه: {0}\n👤 استاد: {1}\n📎 لینک: {2}'
                                          .format(group.title, group.teacher.name, group.link))

        results.append(InlineQueryResultArticle(group.chat_id, title, input_message_content=content))

    # ارسال پاسخ به کاربر
    update.inline_query.answer(results)


def check_group_name(bot, update):
    query = update.callback_query

    logger.info('check group name for {}'.format(query.data))
    # دریافت گروه در حال انتظاری که چت آیدیش مطابقت داشته باشه
    pending_group = PendingGroup.objects.get(chat_id=query.message.chat_id)

    # اگه گروهی پیدا شده بود
    if pending_group is not None:
        # تنظیم نام جدید گروه سایت بر اساس نام فعالی گروه
        pending_group.title = query.message.chat.title
        pending_group.save()
        logger.info('pending group id: <{0}> name changed to <{1}>'.format(pending_group.chat_id,
                                                                           query.message.chat.title))
        # ارسال جواب به کاربر جهت مطلع کردن وی‌
        msg = "❇️ درخواست بررسی مجدد نام گروه شما ثبت گردید. ❇️"
        return bot.edit_message_text(text=msg, chat_id=query.message.chat_id, message_id=query.message.message_id)

    # اگه گروهی پیدا نشده بود
    else:
        logger.warning('cannot find group by id: <{}>'.format(pending_group.chat_id))

        # ارسال پیام به کاربر
        msg = "❌ گروه شما یافت نشد ❌"
        return bot.edit_message_text(text=msg, chat_id=query.message.chat_id, message_id=query.message.message_id)
