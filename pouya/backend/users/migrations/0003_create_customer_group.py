"""Create the 'customer' role group (view-only access to order statuses)."""
from django.db import migrations


def create_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='customer')


def remove_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='customer').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_create_cashier_group'),
    ]

    operations = [
        migrations.RunPython(create_group, remove_group),
    ]
