from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Authentication URLs
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Profile URLs
    path('profile/', views.profile, name='profile'),
    path('profile/update-picture/', views.update_profile_picture, name='update_profile_picture'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('profile/login-history/', views.login_history, name='login_history'),
    path('profile/notifications/', views.notifications, name='notifications'),
    
    # Email Verification URLs
    path('verification-required/', views.verification_required, name='verification_required'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification_email, name='resend_verification'),
    
    # Password Management URLs
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset-confirm/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    
    # Phone Verification URLs
    path('phone-verification/', views.phone_verification_request, name='phone_verification_request'),
    path('verify-phone-otp/', views.verify_phone_otp, name='verify_phone_otp'),
    
    # Two-Factor Authentication URLs
    path('enable-2fa/', views.enable_2fa, name='enable_2fa'),
    path('verify-2fa-setup/', views.verify_2fa_setup, name='verify_2fa_setup'),
    
    # AJAX URLs
    path('ajax/check-username/', views.check_username_availability, name='check_username_availability'),
    path('ajax/check-email/', views.check_email_availability, name='check_email_availability'),
    path('ajax/check-phone/', views.check_phone_availability, name='check_phone_availability'),
]