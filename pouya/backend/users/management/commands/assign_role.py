"""
Assign a user to a single role group (admin, chef, cashier or customer),
replacing any other role group they currently hold.

    python manage.py assign_role <username> <admin|chef|cashier|customer>
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, User

ROLES = ['admin', 'chef', 'cashier', 'customer']


class Command(BaseCommand):
    help = "Assign a user to the 'admin', 'chef', 'cashier' or 'customer' role group."

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
        parser.add_argument('role', type=str, choices=ROLES)

    def handle(self, *args, **options):
        username = options['username']
        role = options['role']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f"User '{username}' does not exist")

        target, _ = Group.objects.get_or_create(name=role)

        # Remove the other role group(s), then add the target one.
        user.groups.remove(*Group.objects.filter(name__in=ROLES).exclude(name=role))
        user.groups.add(target)

        self.stdout.write(self.style.SUCCESS(
            f"User '{username}' is now in role '{role}'."
        ))
