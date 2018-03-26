from django.core.exceptions import ObjectDoesNotExist
from jdatetime import GregorianToJalali
from .app_settings import BOT_ID


def get_group_admins(bot, chat_id):
    """get bot, chat_id
    return: tuple (user Object, user object) => (our_bot, creatorUser)"""
    # تمام ادمین‌های گروه رو دریافت میکنیم
    admins = bot.getChatAdministrators(chat_id)

    our_bot = None
    group_creator = None

    # به ازای هر ادمین موجود در گروه
    for admin in admins:
        # اگر این ادمین ما بودیم
        if admin.user.id == BOT_ID:
            # یعنی ربات ما دسترسی ادمین داشته و می‌توانیم ادامه دهیم
            our_bot = admin
        # اگر ادمین اصلی بود
        if admin.status == 'creator':
            group_creator = admin

    return our_bot, group_creator


def get_model_object(model, chat_id):
    """
    check if chat_id is in the database or note
    :param model: Model (Group, PendingGroup)
    :param chat_id: Int
    :return: Model Object or None on failure.
    """
    model_object = None
    try:
        model_object = model.objects.get(chat_id=chat_id)
    except ObjectDoesNotExist:
        pass
    return model_object


def persian_formatted_date(date):
    gregorian_date = date
    persian_date = GregorianToJalali(gregorian_date.year, gregorian_date.month, gregorian_date.day)

    return '{year:04d}/{month:02d}/{day:02d}'.format(year=persian_date.jyear,
                                                     month=persian_date.jmonth,
                                                     day=persian_date.jday)
