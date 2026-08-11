from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

def manager_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        profile = getattr(request.user, 'staff_profile', None)
        if not profile or not profile.is_manager:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper

def staff_required(view_func):
    """ Any logged-in staff member - manager or regular staff """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        profile = getattr(request.user, 'staff_profile', None)
        if not profile:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper