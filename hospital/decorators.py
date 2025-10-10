    # decorators.py
from django.shortcuts import redirect
from functools import wraps

def role_required(*allowed_roles):
    """
    Decorator to restrict access to users with specified roles.
    Usage:
        @role_required('admin', 'doctor')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role not in allowed_roles:
                # Optionally, redirect to a "Not Authorized" page instead
                return redirect('login')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
