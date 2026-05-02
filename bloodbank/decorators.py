from functools import wraps
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.http import Http404
from django.core.exceptions import PermissionDenied

def admin_required(view_func):
    """
    Decorator to ensure only admin users can access the view
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'role') or request.user.role != 'admin':
            messages.error(request, 'You do not have permission to access this admin feature.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def donor_required(view_func):
    """
    Decorator to ensure only donor users can access the view
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'role') or request.user.role != 'donor':
            messages.error(request, 'Only donors can access this feature.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def patient_required(view_func):
    """
    Decorator to ensure only patient users can access the view
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'role') or request.user.role != 'patient':
            messages.error(request, 'Only patients can access this feature.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def validate_user_role(request, required_role=None):
    """
    Helper function to validate user role
    """
    if not hasattr(request.user, 'role'):
        return False, 'User role not found'
    
    if required_role and request.user.role != required_role:
        return False, f'{required_role.title()} role required'
    
    return True, 'Valid user role'

def validate_object_access(user, obj, action='access'):
    """
    Validate if user can access/modify the object
    """
    # Admin can access everything
    if user.role == 'admin':
        return True, 'Admin access granted'
    
    # Users can only modify their own objects (except admin objects)
    if hasattr(obj, 'user') and obj.user == user:
        return True, 'Self access granted'
    
    if hasattr(obj, 'patient') and obj.patient == user:
        return True, 'Patient access granted'
    
    if hasattr(obj, 'donor') and obj.donor == user:
        return True, 'Donor access granted'
    
    # Donors can access blood requests they're assigned to
    if hasattr(obj, 'assigned_donor') and obj.assigned_donor == user:
        return True, 'Assigned donor access granted'
    
    # Special case: Donors can accept any approved blood request
    if action == 'accept' and user.role == 'donor' and hasattr(obj, 'status') and obj.status == 'approved':
        return True, 'Donor can accept approved requests'
    
    return False, f'Permission denied for {action}'

def validate_blood_stock(blood_group, units_required):
    """
    Validate blood stock availability
    """
    from .models import BloodStock
    
    try:
        blood_stock = BloodStock.objects.get(blood_group=blood_group)
        if blood_stock.units >= units_required:
            return True, blood_stock
        else:
            return False, f'Insufficient stock: {blood_stock.units} units available, {units_required} required'
    except BloodStock.DoesNotExist:
        return False, f'Blood group {blood_group} not found in stock'

def validate_blood_request_status(request, blood_request, new_status):
    """
    Validate blood request status transitions
    """
    current_status = blood_request.status
    
    # Define valid status transitions
    valid_transitions = {
        'admin': {
            'pending': ['approved', 'rejected'],
            'approved': ['fulfilled'],
            'rejected': [],
            'fulfilled': []
        },
        'donor': {
            'pending': [],  # Donors can't change pending requests
            'approved': [],  # Donors can't change approved requests
            'rejected': [],
            'fulfilled': []
        },
        'patient': {
            'pending': ['cancelled'],  # Patients can cancel their own pending requests
            'approved': [],
            'rejected': [],
            'fulfilled': []
        }
    }
    
    user_role = request.user.role
    
    # Check if user can make this transition
    if user_role not in valid_transitions:
        return False, f'Invalid user role: {user_role}'
    
    if new_status not in valid_transitions[user_role].get(current_status, []):
        return False, f'Invalid status transition from {current_status} to {new_status} for {user_role}'
    
    # Additional validations
    if new_status == 'fulfilled':
        # Check if there's enough blood stock
        stock_valid, stock_result = validate_blood_stock(blood_request.blood_group, blood_request.units_required)
        if not stock_valid:
            return False, stock_result
    
    return True, 'Status transition valid'

def sanitize_input(data, allowed_fields):
    """
    Sanitize input data by allowing only specified fields
    """
    sanitized = {}
    for field in allowed_fields:
        if field in data:
            sanitized[field] = data[field]
    return sanitized

def validate_pagination_params(request):
    """
    Validate and sanitize pagination parameters
    """
    try:
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        
        # Validate ranges
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10
            
        return page, per_page
    except (ValueError, TypeError):
        return 1, 10
