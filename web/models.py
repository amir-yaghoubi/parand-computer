from django.db import models
from django.utils.text import slugify
from django.shortcuts import reverse


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
    members = models.PositiveIntegerField(verbose_name='تعداد اعضا', default=0)

    admin_id = models.IntegerField(verbose_name='شناسه ادمین', null=True)
    admin_username = models.CharField(verbose_name='نام کاربری ادمین', max_length=50,  default="تعریف نشده", null=True)

    teacher = models.ForeignKey(Teacher, on_delete='CASCADE')
    category = models.CharField(max_length=1, choices=category_options)

    active = models.BooleanField(verbose_name='فعال', default=False)

    created_date = models.DateTimeField(verbose_name='تاریخ ایجاد', auto_now_add=True)
    approval_date = models.DateTimeField(verbose_name='تاریخ تایید', auto_now_add=True)  # remove auto_now_add

    def _generate_unique_slug(self):
        slug = slugify(self.title + ' ' + str(self.teacher), allow_unicode=True)
        unique_slug = slug
        num = 1

        # تا زمانی که اسلاگ ایجاد شده موجود باشه یکی دیگه می‌سازیم
        while Group.objects.filter(slug=unique_slug).exists():
            unique_slug = f'{slug}-{num}'
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        # TODO test
        # اگه اسلاگ هنوز ایجاد نشده بود
        # تنها در ایجاد رکورد جدید
        # if not self.slug:
        if self.slug == 'no-slug':
            # یک اسلاگ براش تولید بشه
            self.slug = self._generate_unique_slug()

        super().save()

    def get_category_string(self):
        # TODO Test
        cat_name = ''
        for cat in self.category_options:
            if cat[0] == self.category:
                cat_name = cat[1]
                break
        return cat_name

    def get_absolute_url(self):
        kwargs = {'slug': self.slug}
        return reverse('get_group_link', kwargs)

    def __str__(self):
        return '{0}-{1}'.format(self.title, self.get_category_string())

    class Meta:
        verbose_name_plural = "گروه‌ها"
        ordering = ['-approval_date']


class PendingGroup(models.Model):
    chat_id = models.IntegerField(verbose_name='شناسه گروه', primary_key=True)
    title = models.CharField(max_length=200, verbose_name='نام گروه', null=False)
    admin_id = models.IntegerField(verbose_name='شناسه ادمین', null=True)
    admin_username = models.CharField(verbose_name='نام کاربری ادمین', max_length=50,  default="تعریف نشده", null=True)
    created_date = models.DateTimeField(verbose_name='تاریخ ایجاد', auto_now_add=True)

    def __str__(self):
        return f'گروه {self.title} ساخته شده توسط {self.admin_username}'

    class Meta:
        verbose_name_plural = "گروه‌های درحال انتظار"
        ordering = ['-created_date']
