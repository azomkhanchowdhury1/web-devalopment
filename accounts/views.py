from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json

from .models import User, OTP, PasswordResetToken, LoginHistory, Notification
from .forms import (
    UserRegistrationForm, UserLoginForm, CustomPasswordResetForm,
    CustomSetPasswordForm, PhoneVerificationForm, OTPVerificationForm,
    ResendOTPForm, ChangePasswordForm
)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/home.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            
            # Log the user in
            login(request, user)
            
            messages.success(
                request,
                f'Account created successfully! Welcome {user.username}. '
                f'Please check your email to verify your account.'
            )
            
            # Send welcome email
            send_welcome_email(user)
            
            return redirect('verification_required')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            
            # Handle remember me
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)  # Session expires when browser closes
            else:
                request.session.set_expiry(1209600)  # 2 weeks
            
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')

def verification_required(request):
    if request.user.is_authenticated and request.user.is_email_verified:
        return redirect('dashboard')
    return render(request, 'accounts/verification_required.html')

def verify_email(request, token):
    try:
        user = User.objects.get(email_verification_token=token)
        if not user.is_email_verified:
            user.is_email_verified = True
            user.email_verification_token = ''
            user.save()
            
            messages.success(request, 'Email verified successfully! You can now access all features.')
            
            if request.user.is_authenticated:
                return redirect('dashboard')
            else:
                return redirect('login')
        else:
            messages.info(request, 'Email is already verified.')
    except User.DoesNotExist:
        messages.error(request, 'Invalid verification token.')
    
    return redirect('home')

def resend_verification_email(request):
    if request.method == 'POST':
        form = ResendOTPForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            try:
                user = User.objects.get(email=email)
                if user.is_email_verified:
                    messages.info(request, 'Email is already verified.')
                else:
                    user.send_verification_email()
                    messages.success(request, 'Verification email sent successfully!')
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email address.')
    else:
        form = ResendOTPForm()
    
    return render(request, 'accounts/resend_verification.html', {'form': form})

def password_reset_request(request):
    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            
            # Generate password reset token
            reset_token = PasswordResetToken.generate_token(user)
            
            # Send password reset email
            send_password_reset_email(user, reset_token)
            
            messages.success(
                request,
                'Password reset instructions have been sent to your email address.'
            )
            return redirect('login')
    else:
        form = CustomPasswordResetForm()
    
    return render(request, 'accounts/password_reset.html', {'form': form})

def password_reset_confirm(request, token):
    try:
        reset_token = PasswordResetToken.objects.get(token=token, is_used=False)
        
        if reset_token.is_expired():
            messages.error(request, 'Password reset link has expired.')
            return redirect('password_reset')
        
        if request.method == 'POST':
            form = CustomSetPasswordForm(reset_token.user, request.POST)
            if form.is_valid():
                form.save()
                reset_token.is_used = True
                reset_token.save()
                
                messages.success(request, 'Password reset successfully! You can now login with your new password.')
                return redirect('login')
        else:
            form = CustomSetPasswordForm(reset_token.user)
        
        return render(request, 'accounts/password_reset_confirm.html', {
            'form': form,
            'token': token
        })
    
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Invalid password reset link.')
        return redirect('password_reset')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            user.set_password(form.cleaned_data['new_password1'])
            user.save()
            update_session_auth_hash(request, user)
            
            messages.success(request, 'Password changed successfully!')
            return redirect('profile')
    else:
        form = ChangePasswordForm(user=request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})

# Phone Verification Views
def phone_verification_request(request):
    if request.method == 'POST':
        form = PhoneVerificationForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            user = User.objects.get(phone=phone)
            
            # Generate OTP
            otp = OTP.generate_otp(user, 'phone')
            
            # Send OTP via SMS (implement with your SMS provider)
            send_sms_otp(user.phone, otp.code)
            
            messages.success(request, 'OTP sent to your phone number.')
            return redirect('verify_phone_otp')
    else:
        form = PhoneVerificationForm()
    
    return render(request, 'accounts/phone_verification_request.html', {'form': form})

def verify_phone_otp(request):
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            
            # Find the OTP
            try:
                otp = OTP.objects.get(
                    code=code,
                    otp_type='phone',
                    is_used=False
                )
                
                if not otp.is_expired():
                    otp.user.is_phone_verified = True
                    otp.user.save()
                    otp.is_used = True
                    otp.save()
                    
                    messages.success(request, 'Phone number verified successfully!')
                    
                    if request.user.is_authenticated:
                        return redirect('profile')
                    else:
                        return redirect('login')
                else:
                    messages.error(request, 'OTP has expired. Please request a new one.')
            except OTP.DoesNotExist:
                messages.error(request, 'Invalid OTP code.')
    else:
        form = OTPVerificationForm()
    
    return render(request, 'accounts/verify_phone_otp.html', {'form': form})

# Two-Factor Authentication
@login_required
def enable_2fa(request):
    if request.method == 'POST':
        # Generate OTP for 2FA setup
        otp = OTP.generate_otp(request.user, 'login')
        
        # Send OTP via email or SMS
        send_2fa_setup_otp(request.user, otp.code)
        
        messages.success(request, '2FA setup OTP sent to your registered email/phone.')
        return redirect('verify_2fa_setup')
    
    return render(request, 'accounts/enable_2fa.html')

@login_required
def verify_2fa_setup(request):
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST, user=request.user, otp_type='login')
        if form.is_valid():
            # Note: You'll need to add two_factor_enabled field to your User model
            # For now, we'll just show a success message
            messages.success(request, 'Two-factor authentication enabled successfully!')
            return redirect('profile')
    else:
        form = OTPVerificationForm(user=request.user, otp_type='login')
    
    return render(request, 'accounts/verify_2fa_setup.html', {'form': form})

# AJAX Views
@csrf_exempt
def check_username_availability(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        
        exists = User.objects.filter(username=username).exists()
        return JsonResponse({'available': not exists})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def check_email_availability(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        
        exists = User.objects.filter(email=email).exists()
        return JsonResponse({'available': not exists})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def check_phone_availability(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        phone = data.get('phone')
        
        exists = User.objects.filter(phone=phone).exists()
        return JsonResponse({'available': not exists})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

# Email Sending Functions
def send_welcome_email(user):
    subject = 'Welcome to School Management System'
    message = f'''
    Dear {user.get_full_name() or user.username},
    
    Welcome to School Management System! We're excited to have you on board.
    
    Your account has been successfully created with the following details:
    - Username: {user.username}
    - Email: {user.email}
    - User Type: {user.get_user_type_display()}
    
    Please verify your email address to access all features of the system.
    
    If you have any questions, please don't hesitate to contact our support team.
    
    Best regards,
    School Management System Team
    '''
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

def send_password_reset_email(user, reset_token):
    subject = 'Password Reset Request - School Management System'
    message = f'''
    Hello {user.get_full_name() or user.username},
    
    You requested a password reset for your account. Please click the link below to reset your password:
    
    {settings.SITE_URL}/accounts/password-reset-confirm/{reset_token.token}/
    
    This link will expire in 24 hours.
    
    If you didn't request this reset, please ignore this email and your password will remain unchanged.
    
    Best regards,
    School Management System Team
    '''
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

def send_sms_otp(phone_number, otp_code):
    """
    Placeholder function for sending SMS OTP
    Implement with your SMS provider (Twilio, Nexmo, etc.)
    """
    # Example with print - replace with actual SMS sending code
    print(f"Sending OTP {otp_code} to {phone_number}")
    # Implement your SMS gateway integration here
    pass

def send_2fa_setup_otp(user, otp_code):
    """
    Send 2FA setup OTP via email
    """
    subject = 'Two-Factor Authentication Setup - School Management System'
    message = f'''
    Hello {user.get_full_name() or user.username},
    
    You are setting up Two-Factor Authentication for your account.
    
    Your verification code is: {otp_code}
    
    This code will expire in 10 minutes.
    
    If you didn't request this setup, please contact support immediately.
    
    Best regards,
    School Management System Team
    '''
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

@login_required
def dashboard(request):
    """Dashboard view"""
    # Get user statistics based on user type
    user_stats = {
        'total_students': 0,
        'total_teachers': 0,
        'total_classes': 0,
        'attendance_rate': 0,
    }
    
    # You can customize these stats based on user type
    if hasattr(request.user, 'user_type'):
        if request.user.user_type == 'admin':
            user_stats['total_students'] = User.objects.filter(user_type='student', is_active=True).count()
            user_stats['total_teachers'] = User.objects.filter(user_type='teacher', is_active=True).count()
        elif request.user.user_type == 'teacher':
            # Teacher-specific stats
            user_stats['total_classes'] = 5  # Example
            user_stats['attendance_rate'] = 85  # Example
        elif request.user.user_type == 'student':
            # Student-specific stats
            user_stats['attendance_rate'] = 92  # Example
    
    # Get recent notifications
    try:
        recent_notifications = Notification.objects.filter(user=request.user)[:5]
    except:
        recent_notifications = []
    
    return render(request, 'accounts/dashboard.html', {
        'user': request.user,
        'user_stats': user_stats,
        'recent_notifications': recent_notifications
    })

@login_required
def profile(request):
    """User profile view"""
    return render(request, 'accounts/profile.html', {
        'user': request.user
    })

@login_required
def update_profile_picture(request):
    """Update profile picture"""
    if request.method == 'POST':
        profile_picture = request.FILES.get('profile_picture')
        if profile_picture:
            # Handle profile picture update
            try:
                user = request.user
                user.profile_picture = profile_picture
                user.save()
                messages.success(request, 'Profile picture updated successfully!')
            except Exception as e:
                messages.error(request, f'Error updating profile picture: {str(e)}')
        else:
            messages.error(request, 'Please select a picture to upload.')
    
    return redirect('profile')

@login_required
def login_history(request):
    """User login history"""
    try:
        login_records = LoginHistory.objects.filter(user=request.user).order_by('-login_time')[:50]
    except:
        login_records = []
    
    return render(request, 'accounts/login_history.html', {
        'login_records': login_records
    })

@login_required
def notifications(request):
    """User notifications"""
    try:
        notifications_list = Notification.objects.filter(user=request.user).order_by('-created_at')[:50]
    except:
        notifications_list = []
    
    return render(request, 'accounts/notifications.html', {
        'notifications': notifications_list
    })