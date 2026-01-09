from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, UserSettingsForm
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser, PasswordResetOTP
import random

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Send Welcome Email
            subject = 'Welcome to Personal Finance Tracker! 🎉'
            message = f"""Hi {user.username},

Welcome to Personal Finance Tracker! 🎉

Your account has been successfully created, and we’re happy to have you with us.

🔐 What you can do with Personal Finance Tracker
💰 Track your income and expenses
📊 View monthly and yearly financial insights
🔔 Set and monitor monthly budget alerts
🌙 Switch between Dark Mode and Light Mode
🌍 Use region-based currency settings
📁 Export your transactions as CSV

Your financial data is secure, private, and accessible only to you. We are committed to keeping your information safe while helping you manage your money effectively.

Thank you for choosing Personal Finance Tracker — your smart companion for better financial management 💸

Warm regards,
HARISH NAIK"""
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]
            
            try:
                send_mail(subject, message, from_email, recipient_list)
            except Exception as e:
                # Log the error or handle it as needed
                print(f"Error sending email: {e}")

            messages.success(request, f"Account created successfully for {user.username}! Please log in.")
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def settings_view(request):
    if request.method == 'POST':
        form = UserSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings updated successfully!')
            return redirect('settings')
    else:
        form = UserSettingsForm(instance=request.user)
    return render(request, 'users/settings.html', {'form': form})

def forgot_password_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = CustomUser.objects.get(username=username)
            if not user.email:
                messages.error(request, "No email associated with this username. Please contact support.")
                return redirect('forgot_password')
            
            # Generate 6 digit OTP
            otp = str(random.randint(100000, 999999))
            # Delete old OTPs for this user
            PasswordResetOTP.objects.filter(user=user).delete()
            PasswordResetOTP.objects.create(user=user, otp_code=otp)
            
            # Send Email
            subject = 'Password Reset OTP – Personal Finance Tracker'
            message = f"""Hi {user.username},

We received a request to reset your password for your Personal Finance Tracker account.

🔐 Your Password Reset OTP is:
{otp}

This OTP is valid for a short time only.
⚠️ Do not share this OTP with anyone. We will never ask for your OTP or password.

If you did not request a password reset, please ignore this email. Your account will remain secure.

Thank you for helping us keep your account safe.

Warm regards,
HARISH NAIK"""
            
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
            
            request.session['reset_username'] = username
            messages.success(request, f'A 6-digit OTP has been sent to your registered email.')
            return redirect('verify_otp')
        except CustomUser.DoesNotExist:
            messages.error(request, "Username not found.")
    return render(request, 'users/password_reset_request.html')

def verify_otp_view(request):
    username = request.session.get('reset_username')
    if not username:
        return redirect('forgot_password')
        
    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        try:
            user = CustomUser.objects.get(username=username)
            otp_obj = PasswordResetOTP.objects.get(user=user, otp_code=otp_input)
            # Valid OTP
            request.session['otp_verified'] = True
            return redirect('reset_password')
        except (CustomUser.DoesNotExist, PasswordResetOTP.DoesNotExist):
            messages.error(request, "Invalid OTP code. Please try again.")
            
    return render(request, 'users/password_reset_verify.html', {'username': username})

def reset_password_view(request):
    username = request.session.get('reset_username')
    verified = request.session.get('otp_verified')
    
    if not username or not verified:
        return redirect('forgot_password')
        
    if request.method == 'POST':
        pass1 = request.POST.get('password')
        pass2 = request.POST.get('confirm_password')
        
        if len(pass1) < 4:
            messages.error(request, "Password must be at least 4 characters.")
        elif pass1 == pass2:
            user = CustomUser.objects.get(username=username)
            user.set_password(pass1)
            user.save()
            # Clean up
            PasswordResetOTP.objects.filter(user=user).delete()
            del request.session['reset_username']
            del request.session['otp_verified']
            messages.success(request, "Password reset successfully! Please login with your new password.")
            return redirect('login')
        else:
            messages.error(request, "Passwords do not match.")
            
    return render(request, 'users/password_reset_new.html')
