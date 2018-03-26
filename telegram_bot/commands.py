from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from .utils import get_model_object, get_group_admins, persian_formatted_date
from django.shortcuts import reverse
from web.models import PendingGroup, Group
from .decorators import required_verify
import logging
# set logger
logger = logging.getLogger(__name__)


def register(bot, update):
    # پاسخ گویی تنها به سوپر گروه ها
    if update.message.chat.type != 'supergroup':
        update.message.reply_text('❌ امکان ثبت تنها برای ابر گروه‌ها فعال می‌باشد. ❌')
        return

    # بررسی وجود گروه در لیست اصلی سایت
    main_group = get_model_object(Group, update.message.chat_id)
    # در صورتی که در لیست اصلی سایت موجود باشه پیغام مربوطه ارسال میکنیم و روند ثبت گروه جدید رو متوقف میکنیم
    if main_group is not None:
        persian_date = persian_formatted_date(main_group.created_date)

        msg = '✅ گروه شما در سایت ثبت شده است. ✅\n' \
              'تاریخ ثبت: {0}'.format(persian_date)
        update.message.reply_text(msg)
        return

    # بررسی وجود گروه در لیست انتظار سایت
    # در صورتی که گروه در لیست انتظار سایت قرار داشت پیغام مربوطه را ارسال میکنیم و از ادامه فرایند ثبت باز میگردیم.
    pending_group = get_model_object(PendingGroup, update.message.chat_id)
    if pending_group is not None:
        msg = '⏰ در انتظار تایید ⏰\n'\
              'گروه شما در انتظار تایید توسط ادمین‌ سایت می‌باشد.\n'
        update.message.reply_text(msg)
        return

    # در صورتی که تا این قسمت پیش آمده باشیم یعنی گروه باید فرایند ثبت نام را انجام دهد
    # بررسی دسترسی ادمین به بات
    # ثبت گروه در لیست انتظار

    our_bot, group_creator = get_group_admins(bot, update.message.chat_id)
    # اگر بات ما دسترسی ادمین نداشت پیغام خطا و توقف فرایند
    if our_bot is None:
        msg = '⛔️⛔️ خطا ⛔️⛔️\n'\
                '👈🏻 عدم دسترسی به <b>Invite users via link</b> 👉🏻'\
                '\nلطفا ربات تلگرامی ما را ادمین گروه نمایید و دسترسی فوق را برای آن فراهم نمایید.'
        update.message.reply_text(msg, parse_mode=ParseMode.HTML)
        return

    # اگه بات ما دسترسی به لینک گروه نداشت پیغام خطا و توقف فرایند
    if not our_bot.can_invite_users:
        msg = '⛔️⛔️ خطا ⛔️⛔️\n'\
                '👈🏻 عدم دسترسی به <b>Invite users via link</b> 👉🏻'\
                'لطفا پس از فراهم کردن دسترسی فوق مجددا تلاش نمایید. 😉'
        update.message.reply_text(msg, parse_mode=ParseMode.HTML)
        return

    # اضافه کردن گروه به لیست انتظار
    chat = update.message.chat
    PendingGroup.objects.create(title=chat.title, chat_id=chat.id, admin_id=group_creator.user.id,
                                admin_username=group_creator.user.name)

    # ارسال پیام ثبت گروه
    msg = '❇️ گروه شما ثبت گردید. ❇️\n'\
          'بعد از تایید توسط ادمین برای عموم در دسترسی قرار می‌گیرد.\n' \
          '\n' \
          '❗️ توجه ❗️\n' \
          '▪️ نام گروه باید نامی گویا باشد، یعنی شامل نام کامل درس و نام استاد باشد.\n' \
          '▪️ دسترسی‌های خواسته شده برای کارکردن ربات الزامی می‌باشد و در صورتی که بعد از' \
          ' ثبت در سایت دسترسی‌ها گرفته شود گروه شما از سایت حذف می‌گردد.‌'
    update.message.reply_text(msg)


@required_verify
def get_group_information(bot, update, group):
    msg = '📌 گروه: {0}\n'\
          '📎 لینک: {1}\n\n'\
          '👤 استاد: {2}\n'\
          '✉️ ایمیل استاد: {3}'.format(group.title, group.link, group.teacher.name, group.teacher.email)

    bot.sendMessage(update.message.chat_id, msg)


def start(bot, update):
    logger.info('start commands from. chat_id: {0}, chat_type: {1}'.format(
                    update.message.chat.id, update.message.chat.type))

    text = 'سلام! به ربات تلگرامی کامپیوتر پرند خوش آمدید.\n'

    bot.sendMessage(update.message.chat_id, text=text)


def get_help(bot, update):
    help_url = 'https://www.{0}{1}'.format('parand-computer.ir', reverse('web:help'))
    keyboard = [[InlineKeyboardButton('📘 مطالعه بیشتر', help_url)]]
    keyboard_markup = InlineKeyboardMarkup(keyboard)

    help_text = '''جهت اضافه شدن گروه به سایت باید مراحل زیر را انجام دهید
    ۱- گروه را به سوپرگروه ارتقا دهید.
    ۲- ربات تلگرام را به گروه اضافه نمایید.
    ۳- ربات را ادمین گروه کرده و دسترسی invite users via link را به ربات بدهید
    ۴- دستور /register را وارد نمایید تا درخواست شما ثبت گردد.
    گروه شما بعد از تایید توسط ادمین به سایت اضافه خواهد شد.
    
    🔴 توجه: جهت تسریع در روند ثبت حتما قبل از ارسال درخواست نام گروه را به نام درس به همراه نام استاد مربوطه تغییر دهید.'''

    bot.sendMessage(update.message.chat_id, text=help_text, reply_markup=keyboard_markup)


