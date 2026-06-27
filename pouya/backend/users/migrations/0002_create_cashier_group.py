"""Create the 'cashier' role group."""
from django.db import migrations


def create_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='cashier')


def remove_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='cashier').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_create_role_groups'),
    ]

    operations = [
        migrations.RunPython(create_group, remove_group),
    ]
