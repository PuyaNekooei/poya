# Generated manually for Invoice and CartItem models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_id', models.CharField(max_length=100, unique=True, verbose_name='شناسه فاکتور')),
                ('customer_name', models.CharField(blank=True, max_length=200, verbose_name='نام مشتری')),
                ('customer_phone', models.CharField(blank=True, max_length=20, verbose_name='شماره تماس')),
                ('total_amount', models.DecimalField(decimal_places=0, max_digits=12, verbose_name='مبلغ کل')),
                ('status', models.CharField(choices=[('pending', 'در انتظار'), ('paid', 'پرداخت شده'), ('failed', 'ناموفق'), ('cancelled', 'لغو شده')], default='pending', max_length=20, verbose_name='وضعیت')),
                ('payment_method', models.CharField(blank=True, max_length=50, verbose_name='روش پرداخت')),
                ('transaction_id', models.CharField(blank=True, max_length=100, verbose_name='شناسه تراکنش')),
                ('external_data', models.JSONField(blank=True, default=dict, verbose_name='داده\u200cهای خارجی')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')),
                ('order', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invoice', to='orders.order', verbose_name='سفارش')),
            ],
            options={
                'verbose_name': 'فاکتور',
                'verbose_name_plural': 'فاکتورها',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=200, verbose_name='نام محصول')),
                ('product_code', models.CharField(blank=True, max_length=100, verbose_name='کد محصول')),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='تعداد')),
                ('unit_price', models.DecimalField(decimal_places=0, max_digits=12, verbose_name='قیمت واحد')),
                ('total_price', models.DecimalField(decimal_places=0, max_digits=12, verbose_name='قیمت کل')),
                ('product_data', models.JSONField(blank=True, default=dict, verbose_name='داده\u200cهای محصول')),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to='orders.invoice', verbose_name='فاکتور')),
                ('menu_item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='menu.menuitem', verbose_name='آیتم منو')),
            ],
            options={
                'verbose_name': 'آیتم سبد خرید',
                'verbose_name_plural': 'آیتم\u200cهای سبد خرید',
            },
        ),
    ]
