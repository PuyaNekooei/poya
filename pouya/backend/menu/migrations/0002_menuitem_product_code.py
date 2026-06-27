# Generated manually for MenuItem product_code field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='product_code',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='کد محصول'),
        ),
    ]
