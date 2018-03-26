from django.db import models
from django.shortcuts import reverse
from utils.path_convertor import GroupSlug, NormalSlug
from datetime import datetime


class Teacher(models.Model):
    name = models.CharField(max_length=200, verbose_name='نام استاد')
    email = models.EmailField(verbose_name='ایمیل')

    def __str__(self):
        return 'استاد {}'.format(self.name)

    class Meta:
        verbose_name_plural = "اساتید"
        ordering = ['name']


class Group(models.Model):
    category_options = (
        ('T', 'تخصصی'),
        ('A', 'آزمایشگاه'),
        ('O', 'عمومی'),
    )

    title = models.CharField(max_length=200, verbose_name='نام گروه', null=False)
    slug = models.CharField(max_length=300, unique=True, default='no-slug')

    chat_id = models.IntegerField(verbose_name='شناسه گروه', primary_key=True)
    link = models.URLField(verbose_name='لینک گروه')

    admin_id = models.IntegerField(verbose_name='شناسه ادمین', null=True)
    admin_username = models.CharField(verbose_name='نام کاربری ادمین', max_length=50,  default="تعریف نشده", null=True)

    teacher = models.ForeignKey(Teacher, on_delete='CASCADE', verbose_name='نام استاد')
    category = models.CharField(verbose_name='نوع گروه', max_length=1, choices=category_options)

    active = models.BooleanField(verbose_name='نمایش در سایت', default=True)

    created_date = models.DateTimeField(verbose_name='تاریخ ایجاد', auto_now_add=True)

    def _generate_unique_slug(self):
        slug = GroupSlug.slug_it(title=self.title, teacher=str(self.teacher))
        unique_slug = slug
        num = 1
        # تا زمانی که اسلاگ ایجاد شده موجود باشه یکی دیگه می‌سازیم
        while Group.objects.filter(slug=unique_slug).exists():
            unique_slug = '{0}-{1}'.format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        # اگه اسلاگ هنوز ایجاد نشده بود
        # تنها در ایجاد رکورد جدید
        if not self.slug or self.slug == 'no-slug':
            # یک اسلاگ براش تولید بشه
            self.slug = self._generate_unique_slug()

        super().save()

    def __str__(self):
        return '{0}-{1}'.format(self.title, self.get_category_display())

    class Meta:
        verbose_name_plural = "گروه‌ها"
        ordering = ['-created_date']


class PendingGroup(models.Model):
    chat_id = models.IntegerField(verbose_name='شناسه گروه', primary_key=True)
    slug = models.CharField(max_length=300, unique=True)
    title = models.CharField(max_length=200, verbose_name='نام گروه', null=False)
    admin_id = models.IntegerField(verbose_name='شناسه ادمین', null=True)
    admin_username = models.CharField(verbose_name='نام کاربری ادمین', max_length=50,  default="تعریف نشده", null=True)
    created_date = models.DateTimeField(verbose_name='تاریخ ایجاد', auto_now_add=True)
    update_date = models.DateTimeField(verbose_name='آخرین بروزرسانی', auto_now_add=True)

    def _generate_unique_slug(self):
        slug = NormalSlug.slug_it(title=self.title)
        unique_slug = slug
        num = 1
        # تا زمانی که اسلاگ ایجاد شده موجود باشه یکی دیگه می‌سازیم
        while Group.objects.filter(slug=unique_slug).exists():
            unique_slug = '{0}-{1}'.format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        # اگه اسلاگ هنوز ایجاد نشده بود
        # تنها در ایجاد رکورد جدید
        if not self.slug:
            # یک اسلاگ براش تولید بشه
            self.slug = self._generate_unique_slug()

        # تغییر آخرین زمان بروزرسانی به زمان الان
        self.update_date = datetime.now()

        super().save()

    def __str__(self):
        return 'گروه {0} ساخته شده توسط {1}'.format(self.title, self.admin_username)

    class Meta:
        verbose_name_plural = "گروه‌های درحال انتظار"
        ordering = ['-update_date']
