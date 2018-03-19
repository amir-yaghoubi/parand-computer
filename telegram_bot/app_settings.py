from django.conf import settings

# بارگذاری تنظیمات مربوط به بات تلگرام
BOT_TOKEN = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
BOT_ID = getattr(settings, 'TELEGRAM_BOT_ID', -1)
