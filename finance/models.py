from django.db import models
from django.conf import settings
from django.utils import timezone

class Category(models.Model):
    CATEGORY_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense')
    ]
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=CATEGORY_TYPES, default='expense')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, help_text="Null for global categories")

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return f"{self.name} ({self.type})"

class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.description} - {self.amount}"

class Goal(models.Model):
    GOAL_CATEGORIES = [
        ('Emergency Fund', 'Emergency Fund'),
        ('Travel', 'Travel'),
        ('Education', 'Education'),
        ('Home', 'Home'),
        ('Vehicle', 'Vehicle'),
        ('Gadgets', 'Gadgets'),
        ('Other', 'Other')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=50, choices=GOAL_CATEGORIES, default='Other')
    start_date = models.DateField(default=timezone.now)
    target_date = models.DateField(blank=True, null=True)
    saved_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.target_amount}"

class Challenge(models.Model):
    CHALLENGE_TYPES = [
        ('Day', 'No-Spend Day'),
        ('Weekend', 'No-Spend Weekend'),
        ('Month', 'No-Spend Month'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    challenge_type = models.CharField(max_length=20, choices=CHALLENGE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    is_successful = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.challenge_type} ({self.start_date})"

class Badge(models.Model):
    badge_icons = {
        'Day Master': 'fa-calendar-check',
        'Weekend Warrior': 'fa-shield-halved',
        'Month Legend': 'fa-crown',
        'Savings Sensei': 'fa-user-ninja'
    }
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='fa-medal')
    description = models.TextField()
    awarded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.name}"
