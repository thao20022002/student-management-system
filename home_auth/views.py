from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser, PasswordResetRequest
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string


def signup_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        role = request.POST.get('role')  # Get role from the form (student, teacher, or admin)
        
        # Validate required fields
        if not all([first_name, last_name, email, password]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'authentication/register.html')
        
        # Check if passwords match
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'authentication/register.html')
        
        # Check if email already exists
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists. Please use a different email or try logging in.')
            return render(request, 'authentication/register.html')
        
        # Check if username (email) already exists
        if CustomUser.objects.filter(username=email).exists():
            messages.error(request, 'An account with this email already exists. Please use a different email or try logging in.')
            return render(request, 'authentication/register.html')
        
        try:
            # Create the user
            user = CustomUser.objects.create_user(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
            )
            
            # Assign the appropriate role (default to student if no role selected)
            if role == 'student' or not role:
                user.is_student = True
            elif role == 'teacher':
                user.is_teacher = True
            elif role == 'admin':
                user.is_admin = True

            user.save()  # Save the user with the assigned role
            login(request, user)
            messages.success(request, 'Signup successful!')
            return redirect('index')  # Redirect to the index or home page
        
        except Exception as e:
            # Catch any other unexpected errors
            messages.error(request, f'An error occurred during registration. Please try again.')
            return render(request, 'authentication/register.html')
    
    return render(request, 'authentication/register.html')  # Render signup template


def login_view(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email', '').strip()
        password = request.POST['password']
        
        user = None
        
        # Thử authenticate bằng username trước
        user = authenticate(request, username=username_or_email, password=password)
        
        # Nếu không tìm thấy, thử tìm bằng email
        if user is None:
            try:
                user_obj = CustomUser.objects.get(email=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except CustomUser.DoesNotExist:
                pass
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Đăng nhập thành công!')
            
            # Redirect user based on their role
            if user.is_admin:
                # If admin_dashboard URL doesn't exist, redirect to dashboard or index
                return redirect('dashboard')
            elif user.is_teacher:
                # If teacher_dashboard URL doesn't exist, redirect to dashboard or index
                return redirect('dashboard')
            elif user.is_student:
                return redirect('dashboard')
            else:
                # If no role assigned, default to student role and redirect
                user.is_student = True
                user.save()
                messages.info(request, 'Tài khoản của bạn đã được đặt là tài khoản học sinh.')
                return redirect('dashboard')
            
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng!')
    return render(request, 'authentication/login.html')  # Render login template


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
    
    return render(request, 'authentication/forgot-password.html')  # Render forgot password template


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

    return render(request, 'authentication/reset_password.html', {'token': token})  # Render reset password template


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('index')
