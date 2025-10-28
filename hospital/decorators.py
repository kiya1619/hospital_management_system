    # decorators.py
from django.shortcuts import redirect
from functools import wraps
from django.contrib import messages

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
                messages.warning(request, "Please log in to continue.")
                return redirect('login')  # login template must render messages

            if request.user.role not in allowed_roles:
                messages.error(request, "You are not authorized to access this page.")
                return redirect('login')  # login template must render messages

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator