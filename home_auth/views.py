from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser, PasswordResetRequest
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie


def signup_view(request):
    if request.method == 'POST':
    
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        try:
          
            user = CustomUser.objects.create_user(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
            )
            
           
            if role == 'teacher':
                user.is_teacher = True
            elif role == 'admin':
                user.is_admin = True
            else:
                user.is_student = True

          
            user.is_active = True
            user.is_authorized = False
            user.save()
            
      
            messages.success(request, 'Đăng ký thành công! Vui lòng đợi quản trị viên phê duyệt tài khoản.')
            return redirect('login') 
        
        except Exception as e:
            messages.error(request, f'Có lỗi xảy ra trong quá trình đăng ký: {str(e)}')
            return render(request, 'authentication/register.html')
    
    return render(request, 'authentication/register.html')


@never_cache
@ensure_csrf_cookie
@csrf_protect
def login_view(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email', '').strip()
        password = request.POST['password']
        
        
        user = None
        
       
        user = authenticate(request, username=username_or_email, password=password)
        
      
        if user is None:
            try:
                user_obj = CustomUser.objects.get(email=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except CustomUser.DoesNotExist:
                pass
        
       
        if user is not None:
        
            if not user.is_authorized and not user.is_superuser:
                messages.error(request, 'Tài khoản của bạn chưa được phê duyệt. Vui lòng liên hệ Admin.')
                return render(request, 'authentication/login.html')

          
            login(request, user)
            messages.success(request, 'Đăng nhập thành công!')
            
       
            if user.is_admin or user.is_teacher or user.is_student:
                return redirect('dashboard')
            else:
            
                user.is_student = True
                user.save()
                messages.info(request, 'Tài khoản của bạn đã được đặt là tài khoản học sinh.')
                return redirect('dashboard')
            
        else:
          
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng!')
            
    return render(request, 'authentication/login.html')


def csrf_failure(request, reason=''):
    messages.error(
        request,
        'Phiên đăng nhập đã hết hạn hoặc không hợp lệ. Vui lòng tải lại trang và đăng nhập lại.'
    )
    return redirect('login')


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        user = CustomUser.objects.filter(email=email).first()
        
        if user:
            token = get_random_string(32)
            reset_request = PasswordResetRequest.objects.create(user=user, email=email, token=token)
            reset_request.send_reset_email()
            messages.success(request, 'Reset link sent to your email.')
        else:
            messages.error(request, 'Email not found.')
    
    return render(request, 'authentication/forgot-password.html') 


def reset_password_view(request, token):
    reset_request = PasswordResetRequest.objects.filter(token=token).first()
    
    if not reset_request or not reset_request.is_valid():
        messages.error(request, 'Invalid or expired reset link')
        return redirect('index')

    if request.method == 'POST':
        new_password = request.POST['new_password']
        reset_request.user.set_password(new_password)
        reset_request.user.save()
        messages.success(request, 'Password reset successful')
        return redirect('login')

    return render(request, 'authentication/reset_password.html', {'token': token}) 


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('index')
