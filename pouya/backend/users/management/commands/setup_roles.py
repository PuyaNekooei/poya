"""
Ensure the 'admin' and 'chef' role groups exist, give them sensible
Django-admin permissions, and back-fill existing users so nobody is locked
out by the new role-based API permissions.

Run after migrating:

    python manage.py setup_roles

Idempotent — safe to run repeatedly.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType

from menu.models import Category, MenuItem, DailyInventory
from orders.models import Order, OrderItem, Table

# Models the chef role may fully manage (orders + inventory).
CHEF_MODELS = [Order, OrderItem, DailyInventory]
# Models the cashier role may fully manage (orders, no inventory).
CASHIER_MODELS = [Order, OrderItem]
# Admin may manage everything app-related.
ADMIN_MODELS = [Category, MenuItem, DailyInventory, Order, OrderItem, Table]


def perms_for(models):
    cts = ContentType.objects.get_for_models(*models).values()
    return Permission.objects.filter(content_type__in=cts)


class Command(BaseCommand):
    help = "Create admin/chef groups, assign permissions, and back-fill users."

    def handle(self, *args, **options):
        admin_group, _ = Group.objects.get_or_create(name='admin')
        chef_group, _ = Group.objects.get_or_create(name='chef')
        cashier_group, _ = Group.objects.get_or_create(name='cashier')
        # Customers only view order statuses through the API; they need no
        # Django-admin model permissions at all.
        customer_group, _ = Group.objects.get_or_create(name='customer')

        admin_group.permissions.set(perms_for(ADMIN_MODELS))
        chef_group.permissions.set(perms_for(CHEF_MODELS))
        cashier_group.permissions.set(perms_for(CASHIER_MODELS))
        customer_group.permissions.clear()
        self.stdout.write(self.style.SUCCESS(
            f"Groups ready: admin ({admin_group.permissions.count()} perms), "
            f"chef ({chef_group.permissions.count()} perms), "
            f"cashier ({cashier_group.permissions.count()} perms), "
            f"customer ({customer_group.permissions.count()} perms)"
        ))

        # Back-fill: any non-superuser with no role group gets 'admin' so that
        # existing accounts keep their current full access. Reassign to 'chef'
        # later with: python manage.py assign_role <username> chef
        backfilled = []
        for user in User.objects.filter(is_superuser=False):
            if not user.groups.filter(name__in=['admin', 'chef', 'cashier', 'customer']).exists():
                user.groups.add(admin_group)
                backfilled.append(user.username)

        if backfilled:
            self.stdout.write(self.style.WARNING(
                "Assigned 'admin' role to existing ungrouped users: "
                + ", ".join(backfilled)
            ))
        else:
            self.stdout.write("No ungrouped users to back-fill.")
