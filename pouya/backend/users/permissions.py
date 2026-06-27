"""
Role-based permissions backed by Django groups.

Roles used across the app:
  - ``admin``    : full access to everything.
  - ``chef``     : manage orders and daily inventory only (read-only elsewhere).
  - ``cashier``  : manage orders and invoices only (no inventory; read-only elsewhere).
  - ``customer`` : view-only access to order statuses (no management at all).

Superusers always pass every check regardless of group membership.
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS

ADMIN_GROUP = 'admin'
CHEF_GROUP = 'chef'
CASHIER_GROUP = 'cashier'
CUSTOMER_GROUP = 'customer'

# All roles, in priority order (used by role_of() to pick a primary role).
ROLE_GROUPS = [ADMIN_GROUP, CHEF_GROUP, CASHIER_GROUP, CUSTOMER_GROUP]


def in_group(user, *group_names):
    """True if the authenticated user is a superuser or belongs to any group."""
    if not (user and user.is_authenticated):
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=group_names).exists()


def role_of(user):
    """Return the primary role name for a user (used by the API responses)."""
    if not (user and user.is_authenticated):
        return None
    if user.is_superuser or user.groups.filter(name=ADMIN_GROUP).exists():
        return ADMIN_GROUP
    user_groups = set(user.groups.values_list('name', flat=True))
    for role in (CHEF_GROUP, CASHIER_GROUP, CUSTOMER_GROUP):
        if role in user_groups:
            return role
    return None


class IsAdmin(BasePermission):
    """Only members of the admin group (or superusers)."""

    def has_permission(self, request, view):
        return in_group(request.user, ADMIN_GROUP)


class IsAdminOrChef(BasePermission):
    """Members of the admin or chef group. Full read/write for both."""

    def has_permission(self, request, view):
        return in_group(request.user, ADMIN_GROUP, CHEF_GROUP)


class IsOrderStaff(BasePermission):
    """Any staff that handles orders: admin, chef or cashier. Full read/write."""

    def has_permission(self, request, view):
        return in_group(request.user, ADMIN_GROUP, CHEF_GROUP, CASHIER_GROUP)


class IsOrderViewer(BasePermission):
    """Anyone allowed to *view* order statuses: order staff plus customers."""

    def has_permission(self, request, view):
        return in_group(request.user, ADMIN_GROUP, CHEF_GROUP, CASHIER_GROUP, CUSTOMER_GROUP)


class IsAdminOrReadOnly(BasePermission):
    """Any authenticated user may read; only admins may write."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return in_group(request.user, ADMIN_GROUP)
