# Generated manually to fix Invoice.order and Order.invoice related_name

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_order_type_invoice_orderitem_product_info'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='order',
            field=models.OneToOneField(blank=True, null=True, on_delete=models.SET_NULL, related_name='related_invoice', to='orders.order', verbose_name='سفارش'),
        ),
        migrations.AlterField(
            model_name='order',
            name='invoice',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='orders', to='orders.invoice', verbose_name='فاکتور خارجی'),
        ),
    ]
