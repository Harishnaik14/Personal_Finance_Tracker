from django import forms
from django.db import models
from .models import Transaction, Category, Goal

class TransactionForm(forms.ModelForm):
    custom_category = forms.CharField(required=False, label="Custom Category (if Other)", widget=forms.TextInput(attrs={'placeholder': 'Enter new category name'}))

    class Meta:
        model = Transaction
        fields = ['category', 'custom_category', 'amount', 'date', 'description']
        labels = {
            'category': 'Categories'
        }
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'required': True, 'rows': 3}),
        }
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter: Global or User Specific (if user exists)
        if user:
            qs = Category.objects.filter(
                models.Q(user=None) | models.Q(user=user)
            ).order_by('type', 'name')
        else:
            qs = Category.objects.filter(user=None).order_by('type', 'name')
        
        # Grouping categories for the select widget
        income_cats = [(c.id, c.name) for c in qs if c.type == 'income']
        expense_cats = [(c.id, c.name) for c in qs if c.type == 'expense']
        
        self.fields['category'].choices = [
            ('', '---------'),
            ('Income Sources', income_cats),
            ('Expense Categories', expense_cats),
        ]
        
        self.fields['description'].required = True

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        custom_name = cleaned_data.get('custom_category')
        
        if category and category.name == 'Other' and not custom_name:
            self.add_error('custom_category', 'Please specify the category name.')
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        category = self.cleaned_data.get('category')
        custom_name = self.cleaned_data.get('custom_category')
        
        if category and category.name == 'Other' and custom_name:
            # Create new category for this user, matching the type of the 'Other' selected
            new_cat, created = Category.objects.get_or_create(
                name=custom_name,
                user=instance.user,
                type=category.type
            )
            instance.category = new_cat
            
        if commit:
            instance.save()
        return instance

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['name', 'target_amount', 'category', 'start_date', 'target_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'target_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ExportForm(forms.Form):
    REPORT_FORMATS = [
        ('csv', 'CSV (Excel/Sheets)'),
        ('pdf', 'PDF (Document)'),
        ('word', 'Word (.docx)'),
    ]
    
    file_name = forms.CharField(
        max_length=100, 
        initial="Financial_Report",
        widget=forms.TextInput(attrs={'placeholder': 'Enter file name'})
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    format = forms.ChoiceField(choices=REPORT_FORMATS, initial='csv')
    include_transactions = forms.BooleanField(
        required=False,
        initial=True,
        label="Include Transaction Details",
        help_text="Uncheck to generate a summary-only report"
    )
