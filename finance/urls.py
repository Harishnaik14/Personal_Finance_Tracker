from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/add/', views.transaction_create, name='transaction_create'),
    path('transactions/<int:pk>/edit/', views.transaction_update, name='transaction_update'),
    path('transactions/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),
    path('simulate/', views.simulate_payment, name='simulate_payment'),
    path('overview/', views.overview, name='overview'),
    path('income-vs-expense/', views.income_vs_expense, name='income_vs_expense'),
    path('calendar/', views.calendar_view, name='calendar_view'),
    path('export/', views.export_data, name='export_data'),
    path('goals/', views.goal_list, name='goal_list'),
    path('goals/<int:pk>/add-money/', views.goal_add_money, name='goal_add_money'),
    path('goals/<int:pk>/delete/', views.goal_delete, name='goal_delete'),
    path('challenges/', views.challenge_list, name='challenge_list'),
    path('challenges/start/', views.start_challenge, name='start_challenge'),
]
