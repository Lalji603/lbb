from django import template
from ..models import User

register = template.Library()

@register.filter
def filter_by_role(users, role):
    """Filter users by role"""
    # Convert to list if it's a QuerySet to avoid slice issues
    if hasattr(users, 'filter'):
        return users.filter(role=role)
    return [user for user in users if user.role == role]

@register.filter
def filter_verified(users, is_verified):
    """Filter users by verification status"""
    # Convert to list if it's a QuerySet to avoid slice issues
    if hasattr(users, 'filter'):
        return users.filter(is_verified=is_verified)
    return [user for user in users if user.is_verified == is_verified]
