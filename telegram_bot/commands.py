import logging
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from web.models import PendingGroup
from .app_settings import BOT_ID
from django.shortcuts import reverse
# set logger
logger = logging.getLogger(__name__)


def get_id(bot, update):
    logger.info('chat_id:{} requested their chat id. chat type: {}'.format(
                    update.message.chat.id, update.message.chat.type))

    chat = bot.get_chat(update.message.chat_id)
    update.message.reply_text('chat_id: {0}\nchat_type: {1}'.format(chat.id, chat.type))


def _group_admins(bot, chat_id):
    """get bot, chat_id
    return: tuple (boolean, user object) => (isBotAdmin, creatorUser)"""
    # تمام ادمین‌های گروه رو دریافت میکنیم
    admins = bot.getChatAdministrators(chat_id)

    is_admin = False
    group_creator = None

    # به ازای هر ادمین موجود در گروه
    for admin in admins:
        # اگر این ادمین ما بودیم
        if admin.user.id == BOT_ID:
            # یعنی ربات ما دسترسی ادمین داشته و می‌توانیم ادامه دهیم
            is_admin = True
        # اگر ادمین اصلی بود
        if admin.status == 'creator':
            group_creator = admin

    return is_admin, group_creator


def add(bot, update):
    # در صورتی که پیام ارسالی از سوپرگروه بود
    if update.message.chat.type == 'supergroup':
        is_admin, group_creator = _group_admins(bot, update.message.chat_id)

        # اگر بات ما دسترسی ادمین نداشت
        if not is_admin:
            update.message.reply_text('ابتدا دسترسی ادمین به بات داده و سپس دوباره تلاش نمایید.')
            return

        chat = update.message.chat
        exist_gp = PendingGroup.objects.filter(chat_id=chat.id).first()
        if not exist_gp:
            new_group = PendingGroup(title=chat.title, chat_id=chat.id,
                                     admin_id=group_creator.user.id, admin_username=group_creator.user.username)
            new_group.save()
            update.message.reply_text(
                'گروه شما در لیست انتظار قرار گرفت، بعد از تایید توسط مدیران به سایت اضافه می‌گردد.')
        elif exist_gp.approved:
            update.message.reply_text(
                'گروه شما با موفقیت در سایت قرار گرفته است.')
        else:
            update.message.reply_text(
                'گروه شما در انتظار تایید توسط مدیران قرار دارد، از شکیبایی شما سپاس گذاریم.')


def start(bot, update):
    logger.info('start commands from. chat_id: {0}, chat_type: {1}'
      .format(update.message.chat.id, update.message.chat.type))

    if update.message.chat.type == 'supergroup':
        reply_keyboard = [['افزودن گروه به سایت', 'راهنما']]
    else:
        reply_keyboard = [['/get_id', '/hi', '/help']]
    
    text = 'سلام خوش‌آمدید، این بات در حال توسعه می‌باشد.'
    bot.sendMessage(update.message.chat_id, text=text,
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))


def get_help(bot, update):
    # TODO better url making i guess
    help_url = 'http://www.{0}{1}'.format('localhost:8000', reverse('help'))
    keyboard = [[InlineKeyboardButton('📘 مطالعه بیشتر', help_url)]]
    keyboard_markup = InlineKeyboardMarkup(keyboard)

    help_text = '''جهت اضافه شدن گروه به سایت باید مراحل زیر را انجام دهید
    ۱- گروه را به سوپرگروه ارتقا دهید.
    ۲- ربات تلگرام را به گروه اضافه نمایید.
    ۳- ربات را ادمین گروه کرده و دسترسی invite users via link را به ربات بدهید
    ۴- دستور /register را وارد نمایید تا درخواست شما ثبت گردد.
    گروه شما بعد از تایید توسط ادمین سایت به سایت اضافه خواهد شد.
    
    🔴 توجه: جهت تسریع در روند ثبت حتما قبل از ارسال درخواست نام گروه را به نام درس به همراه نام استاد مربوطه تغییر دهید.'''

    bot.sendMessage(update.message.chat_id, text=help_text, reply_markup=keyboard_markup)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)
