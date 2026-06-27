from django.db import models
from django.utils.translation import gettext_lazy as _
from decimal import Decimal


class Category(models.Model):
    name = models.CharField(_('نام دسته‌بندی'), max_length=100)
    description = models.TextField(_('توضیحات'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('دسته‌بندی')
        verbose_name_plural = _('دسته‌بندی‌ها')

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    VAT_RATE_CHOICES = [
        (0, _('بدون مالیات (0%)')),
        (10, _('مالیات 10%')),
        (16, _('مالیات 16%')),
    ]
    
    name = models.CharField(_('نام غذا'), max_length=100)
    product_code = models.CharField(_('کد محصول'), max_length=50, unique=True, blank=True, null=True)
    description = models.TextField(_('توضیحات'), blank=True)
    price_without_tax = models.DecimalField(_('قیمت بدون مالیات'), max_digits=10, decimal_places=2)
    vat_rate = models.IntegerField(_('نرخ مالیات بر ارزش افزوده'), choices=VAT_RATE_CHOICES, default=10, 
                                    help_text=_('درصد مالیات بر ارزش افزوده'))
    price_with_tax = models.DecimalField(_('قیمت با مالیات'), max_digits=10, decimal_places=2, blank=True, null=True, editable=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='menu_items', verbose_name=_('دسته‌بندی'))
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)
    is_available = models.BooleanField(_('موجود است'), default=True)
    is_active = models.BooleanField(_('فعال است'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def price(self):
        return self.price_with_tax

    class Meta:
        verbose_name = _('غذا')
        verbose_name_plural = _('غذاها')

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Automatically calculate price_with_tax based on vat_rate
        if self.price_without_tax:
            vat_multiplier = Decimal('1') + (Decimal(str(self.vat_rate)) / Decimal('100'))
            self.price_with_tax = self.price_without_tax * vat_multiplier
        super().save(*args, **kwargs)


class DailyInventory(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='daily_inventory', verbose_name=_('غذا'))
    quantity_available = models.PositiveIntegerField(_('موجودی'))
    date = models.DateField(_('تاریخ'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('موجودی روزانه')
        verbose_name_plural = _('موجودی‌های روزانه')
        unique_together = ('menu_item', 'date')

    def __str__(self):
        return f"{self.menu_item.name} - {self.date}"
