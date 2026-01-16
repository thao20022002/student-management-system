from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden

def admin_required(view_func):

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Bạn cần đăng nhập để truy cập trang này!")
            return redirect('login')
        if not request.user.is_admin:
            messages.error(request, "Bạn không có quyền truy cập trang này! Chỉ admin mới có quyền.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def teacher_required(view_func):

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Bạn cần đăng nhập để truy cập trang này!")
            return redirect('login')
        if not (request.user.is_teacher or request.user.is_admin):
            messages.error(request, "Bạn không có quyền truy cập trang này! Chỉ giáo viên và admin mới có quyền.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def student_required(view_func):

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Bạn cần đăng nhập để truy cập trang này!")
            return redirect('login')
        if not request.user.is_student:
            messages.error(request, "Bạn không có quyền truy cập trang này! Chỉ học sinh mới có quyền.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_or_teacher_required(view_func):

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Bạn cần đăng nhập để truy cập trang này!")
            return redirect('login')
        if not (request.user.is_admin or request.user.is_teacher):
            messages.error(request, "Bạn không có quyền truy cập trang này!")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view





