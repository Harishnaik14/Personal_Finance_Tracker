import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finance_manager.settings')
django.setup()

from finance.models import Category

def seed_categories():
    categories = [
        ('Salary', 'income'),
        ('Business', 'income'),
        ('Investment', 'income'),
        ('Other', 'income'),
        ('Food', 'expense'),
        ('Travel', 'expense'),
        ('Rent', 'expense'),
        ('Shopping', 'expense'),
        ('Bills', 'expense'),
        ('Entertainment', 'expense'),
        ('Health', 'expense'),
        ('Education', 'expense'),
    ]

    for name, type_ in categories:
        Category.objects.get_or_create(name=name, type=type_, user=None)
    
    print("Categories seeded successfully!")

if __name__ == '__main__':
    seed_categories()
    