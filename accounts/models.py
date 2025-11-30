from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    designation = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} Profile"

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent'),
        ('accountant', 'Accountant'),
    )
    
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='student')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    bio = models.TextField(blank=True)
    
    # Verification fields
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True)
    phone_verification_code = models.CharField(max_length=6, blank=True)
    phone_verification_sent_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

    def get_profile_picture_url(self):
        """Return profile picture URL or default"""
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        return f'https://ui-avatars.com/api/?name={self.username}&background=random'

    
    def generate_verification_token(self):
        """Generate email verification token"""
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        self.email_verification_token = token
        self.save()
        return token
    
    def generate_phone_verification_code(self):
        """Generate 6-digit phone verification code"""
        code = ''.join(random.choices(string.digits, k=6))
        self.phone_verification_code = code
        self.phone_verification_sent_at = timezone.now()
        self.save()
        return code
    
    def send_verification_email(self):
        """Send email verification link"""
        token = self.generate_verification_token()
        subject = 'Verify Your Email - School Management System'
        message = f'''
        Hello {self.get_full_name() or self.username},
        
        Please verify your email address by clicking the link below:
        
        {settings.SITE_URL}/accounts/verify-email/{token}/
        
        If you didn't create an account, please ignore this email.
        
        Best regards,
        School Management System Team
        '''
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            fail_silently=False,
        )
    
    def send_phone_verification_code(self):
        """Send phone verification code (implement with SMS gateway)"""
        code = self.generate_phone_verification_code()
        # Implement SMS sending logic here
        # This is a placeholder - integrate with your SMS provider
        print(f"Phone verification code for {self.phone}: {code}")
        return code
    
    def is_phone_verification_code_expired(self):
        """Check if phone verification code is expired (10 minutes)"""
        if not self.phone_verification_sent_at:
            return True
        expiration_time = self.phone_verification_sent_at + timezone.timedelta(minutes=10)
        return timezone.now() > expiration_time

class OTP(models.Model):
    OTP_TYPE_CHOICES = (
        ('email', 'Email Verification'),
        ('phone', 'Phone Verification'),
        ('password_reset', 'Password Reset'),
        ('login', 'Login Verification'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_type = models.CharField(max_length=20, choices=OTP_TYPE_CHOICES)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.otp_type} - {self.code}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        return not self.is_used and not self.is_expired()
    
    @classmethod
    def generate_otp(cls, user, otp_type, expiry_minutes=10):
        """Generate OTP for user"""
        # Delete existing unused OTPs of same type
        cls.objects.filter(user=user, otp_type=otp_type, is_used=False).delete()
        
        code = ''.join(random.choices(string.digits, k=6))
        expires_at = timezone.now() + timezone.timedelta(minutes=expiry_minutes)
        
        otp = cls.objects.create(
            user=user,
            otp_type=otp_type,
            code=code,
            expires_at=expires_at
        )
        return otp

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Password reset for {self.user.username}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        return not self.is_used and not self.is_expired()
    
    @classmethod
    def generate_token(cls, user):
        """Generate password reset token"""
        # Delete existing unused tokens
        cls.objects.filter(user=user, is_used=False).delete()
        
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=50))
        expires_at = timezone.now() + timezone.timedelta(hours=24)
        
        reset_token = cls.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        return reset_token
    

class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.CharField(max_length=50, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    login_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-login_time']

    def __str__(self):
        return f"{self.user.username} logged in at {self.login_time}"


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('success', 'Success'),
        ('alert', 'Alert'),
        ('message', 'Message'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"



