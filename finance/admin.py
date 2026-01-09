from django.contrib import admin
from .models import Category, Transaction, Goal, Challenge, Badge

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'user')
    list_filter = ('type', 'user')
    search_fields = ('name',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('description', 'amount', 'get_type', 'date', 'user', 'category')
    list_filter = ('category__type', 'date', 'user', 'category')
    search_fields = ('description', 'user__username', 'user__first_name', 'user__last_name')

    def get_type(self, obj):
        return obj.category.type
    get_type.short_description = 'Type'

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('name', 'target_amount', 'saved_amount', 'user', 'target_date')
    list_filter = ('user', 'category')
    search_fields = ('name', 'user__username')

@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge_type', 'start_date', 'end_date', 'is_active', 'is_successful')
    list_filter = ('challenge_type', 'is_active', 'is_successful')
    search_fields = ('user__username',)

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'awarded_at')
    list_filter = ('name',)
    search_fields = ('user__username', 'name')
