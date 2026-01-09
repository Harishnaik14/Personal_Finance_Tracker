from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    REGION_CHOICES = [
        ('USD', 'USA ($)'),
        ('INR', 'India (₹)'),
        ('GBP', 'UK (£)'),
        ('EUR', 'Europe (€)'),
        ('JPY', 'Japan (¥)'),
    ]
    # Storing currency code as the primary 'region' or 'currency' preference
    currency = models.CharField(max_length=3, choices=REGION_CHOICES, default='USD')
    theme_preference = models.CharField(max_length=10, default='light', choices=[('light', 'Light Mode'), ('dark', 'Dark Mode')])
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text="Your starting balance when you began using the app")
    
    # We can label this 'region' in the UI but store the ISO currency code for easier logic
    # Or strict region choices mapping to currency. Let's do currency primarily.
    
    def __str__(self):
        return self.username

    @property
    def currency_symbol(self):
        symbols = {
            'USD': '$',
            'INR': '₹',
            'GBP': '£',
            'EUR': '€',
            'JPY': '¥',
        }
        return symbols.get(self.currency, '$')

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OTP for {self.user.username}"

class LoginHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Login Histories"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.ip_address} at {self.timestamp}"
