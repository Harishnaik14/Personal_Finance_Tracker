from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import LoginHistory
import logging

logger = logging.getLogger(__name__)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@receiver(user_logged_in)
def track_login_history(sender, request, user, **kwargs):
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
    
    # Check if this IP and User Agent combo is already known
    known_login = LoginHistory.objects.filter(
        user=user, 
        ip_address=ip_address, 
        user_agent=user_agent
    ).exists()
    
    if not known_login:
        # Send alert email
        subject = 'Security Alert: New Login Detected'
        message = f'Hi {user.username},\n\nWe detected a login to your account from a new device or location:\n\n' \
                  f'IP Address: {ip_address}\n' \
                  f'Device/Browser: {user_agent}\n\n' \
                  f'If this was you, you can ignore this email. If not, please change your password immediately.'
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Failed to send suspicious login alert: {e}")
    
    # Log the login
    LoginHistory.objects.create(
        user=user,
        ip_address=ip_address,
        user_agent=user_agent
    )
