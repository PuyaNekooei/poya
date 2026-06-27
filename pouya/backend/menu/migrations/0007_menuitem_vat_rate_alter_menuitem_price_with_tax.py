# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0006_remove_menuitem_price_menuitem_price_without_tax'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='vat_rate',
            field=models.IntegerField(choices=[(0, 'بدون مالیات (0%)'), (10, 'مالیات 10%'), (16, 'مالیات 16%)')], default=10, help_text='درصد مالیات بر ارزش افزوده', verbose_name='نرخ مالیات بر ارزش افزوده'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='price_with_tax',
            field=models.DecimalField(blank=True, decimal_places=2, editable=False, max_digits=10, null=True, verbose_name='قیمت با مالیات'),
        ),
    ]



