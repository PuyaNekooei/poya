# Generated manually for CartItem product_id and menu_info fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_invoice_cartitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='product_id',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='شناسه محصول'),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='menu_info',
            field=models.JSONField(blank=True, default=dict, help_text='اطلاعات منو برای محصولات بدون تطبیق', verbose_name='اطلاعات منو'),
        ),
    ]
