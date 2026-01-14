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
        # ... (giữ nguyên phần lấy dữ liệu và validate) ...
        
        try:
            # Tạo user
            user = CustomUser.objects.create_user(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
            )
            
            # Thiết lập quyền (giữ nguyên logic role của bạn)
            if role == 'teacher':
                user.is_teacher = True
            elif role == 'admin':
                user.is_admin = True
            else:
                user.is_student = True

            # QUAN TRỌNG: Đặt tài khoản ở trạng thái chờ duyệt
            user.is_active = False 
            user.save()
            
            # XÓA dòng login(request, user) để người dùng không vào được hệ thống ngay
            messages.success(request, 'Đăng ký thành công! Vui lòng đợi quản trị viên phê duyệt tài khoản.')
            return redirect('login') # Chuyển hướng về trang đăng nhập
        
        except Exception as e:
            messages.error(request, f'Có lỗi xảy ra trong quá trình đăng ký.')
            return render(request, 'authentication/register.html')
    
    return render(request, 'authentication/register.html')


def login_view(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email', '').strip()
        password = request.POST['password']
        
        # KHỞI TẠO biến user để tránh lỗi NameError
        user = None
        
        # 1. Thử xác thực bằng username trước
        user = authenticate(request, username=username_or_email, password=password)
        
        # 2. Nếu không tìm thấy bằng username, thử tìm bằng email
        if user is None:
            try:
                user_obj = CustomUser.objects.get(email=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except CustomUser.DoesNotExist:
                pass
        
        # 3. Kiểm tra xem user có tồn tại (xác thực thành công) hay không
        if user is not None:
            # KIỂM TRA QUYỀN: Tài khoản phải được Admin duyệt (is_authorized=True)
            if not user.is_authorized:
                messages.error(request, 'Tài khoản của bạn chưa được phê duyệt. Vui lòng liên hệ Admin.')
                return render(request, 'authentication/login.html')

            # Nếu đã duyệt, tiến hành đăng nhập
            login(request, user)
            messages.success(request, 'Đăng nhập thành công!')
            
            # Điều hướng dựa trên vai trò (Role)
            if user.is_admin or user.is_teacher or user.is_student:
                return redirect('dashboard')
            else:
                # Mặc định gán quyền học sinh nếu chưa có vai trò
                user.is_student = True
                user.save()
                messages.info(request, 'Tài khoản của bạn đã được đặt là tài khoản học sinh.')
                return redirect('dashboard')
            
        else:
            # Nếu authenticate trả về None
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng!')
            
    return render(request, 'authentication/login.html')


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
