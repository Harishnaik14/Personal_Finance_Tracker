from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, PasswordResetOTP, LoginHistory
from finance.models import Badge, Category, Challenge, Goal, Transaction

class BadgeInline(admin.TabularInline):
    model = Badge
    extra = 0
    can_delete = False
    
class CategoryInline(admin.TabularInline):
    model = Category
    extra = 0
    can_delete = False

class ChallengeInline(admin.TabularInline):
    model = Challenge
    extra = 0
    can_delete = False

class GoalInline(admin.TabularInline):
    model = Goal
    extra = 0
    can_delete = False

class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    can_delete = False

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'currency', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('currency',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('currency',)}),
    )
    inlines = [BadgeInline, CategoryInline, ChallengeInline, GoalInline, TransactionInline]

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(PasswordResetOTP)

@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'timestamp', 'user_agent')
    list_filter = ('timestamp', 'user')
    search_fields = ('user__username', 'ip_address')
