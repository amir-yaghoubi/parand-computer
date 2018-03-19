from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import Teacher, Group, PendingGroup

# اضافه کردن مدل‌ها به پنل ادمین
admin.site.register(Teacher)
admin.site.register(Group)
admin.site.register(PendingGroup)
