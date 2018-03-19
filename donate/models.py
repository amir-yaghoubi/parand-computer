from django.db import models


class Donate(models.Model):
    name = models.CharField(max_length=200, default='نامشخص', verbose_name='نام')
    amount = models.PositiveIntegerField(default=0, verbose_name='مبلغ واریزی')
    reference_id = models.CharField(max_length=100, verbose_name='شماره ارجاع')

    class Meta:
        verbose_name_plural = "اهدا کننده‌ها"
        ordering = ['amount']
