# Generated manually for Order order_type, invoice FK and OrderItem product_info

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_cartitem_product_id_menu_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_type',
            field=models.CharField(choices=[('manual', 'دستی'), ('ussd', 'سیستم USSD')], default='manual', max_length=20, verbose_name='نوع سفارش'),
        ),
        migrations.AddField(
            model_name='order',
            name='invoice',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, to='orders.invoice', verbose_name='فاکتور خارجی'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='menu_item',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.CASCADE, to='menu.menuitem', verbose_name='آیتم منو'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='product_info',
            field=models.JSONField(blank=True, default=dict, help_text='اطلاعات محصول برای آیتم‌های بدون تطبیق منو', verbose_name='اطلاعات محصول'),
        ),
    ]
