from typing import Any


from django.db import models
from django.contrib.auth.models import User
from menu.models import MenuItem
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import json
import jdatetime


class Table(models.Model):
    """A dine-in restaurant table that manual orders can be assigned to."""
    TABLE_STATUS_CHOICES = [
        ('free', _('آزاد')),
        ('occupied', _('اشغال شده')),
        ('reserved', _('رزرو شده')),
    ]

    number = models.PositiveIntegerField(_('شماره میز'), unique=True)
    name = models.CharField(_('نام میز'), max_length=100, blank=True)
    capacity = models.PositiveIntegerField(_('ظرفیت'), default=4)
    status = models.CharField(_('وضعیت'), max_length=20, choices=TABLE_STATUS_CHOICES, default='free')
    is_active = models.BooleanField(_('فعال است'), default=True)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)

    class Meta:
        verbose_name = _('میز')
        verbose_name_plural = _('میزها')
        ordering = ['number']

    def __str__(self):
        return self.name or f"میز {self.number}"


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', _('در انتظار')),
        ('preparing', _('در حال آماده‌سازی')),
        ('ready', _('آماده')),
        ('completed', _('تکمیل شده')),
        ('cancelled', _('لغو شده')),
    ]
    
    ORDER_TYPE_CHOICES = [
        ('manual', _('دستی')),
    ]

    order_number = models.CharField(_('شماره سفارش'), max_length=20, unique=True)
    customer_name = models.CharField(_('نام مشتری'), max_length=200, blank=True)
    customer_phone = models.CharField(_('شماره تماس مشتری'), max_length=20, blank=True)
    total_amount = models.DecimalField(_('مبلغ کل'), max_digits=10, decimal_places=2, default=0)
    status = models.CharField(_('وضعیت'), max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    order_type = models.CharField(_('نوع سفارش'), max_length=20, choices=ORDER_TYPE_CHOICES, default='manual')
    notes = models.TextField(_('یادداشت'), blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders_created', verbose_name=_('ایجادکننده'))
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)

    # Dine-in table (manual orders only; takeaway leaves it blank)
    table = models.ForeignKey('Table', on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='orders', verbose_name=_('میز'))

    class Meta:
        verbose_name = _('سفارش')
        verbose_name_plural = _('سفارش‌ها')

    def __str__(self):
        return f"Order #{self.order_number} - {self.customer_name}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number based on Jalali date and sequence
            today = timezone.now().date()
            jalali_date = jdatetime.date.fromgregorian(date=today)
            today_orders = Order.objects.filter(created_at__date=today).count()
            self.order_number = f"ORD-{jalali_date.strftime('%Y%m%d')}-{1000+today_orders + 1:03d}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name=_('سفارش'))
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('آیتم منو'))
    quantity = models.PositiveIntegerField(_('تعداد'), default=1)
    unit_price = models.DecimalField(_('قیمت واحد'), max_digits=10, decimal_places=2)
    total_price = models.DecimalField(_('قیمت کل'), max_digits=10, decimal_places=2)
    notes = models.CharField(_('یادداشت'), max_length=200, blank=True)
    
    # Store product info as JSON if no menu_item match
    product_info = models.JSONField(_('اطلاعات محصول'), default=dict, blank=True,
                                   help_text=_('اطلاعات محصول برای آیتم‌های بدون تطبیق منو'))
    
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)

    class Meta:
        verbose_name = _('آیتم سفارش')
        verbose_name_plural = _('آیتم‌های سفارش')

    def __str__(self):
        if self.menu_item:
            return f"{self.quantity}x {self.menu_item.name} - Order #{self.order.order_number}"
        else:
            product_name = self.product_info.get('product_name', 'Unknown Product')
            return f"{self.quantity}x {product_name} - Order #{self.order.order_number}"

    def save(self, *args, **kwargs):
        if not self.unit_price and self.menu_item:
            self.unit_price = self.menu_item.price_with_tax
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)
