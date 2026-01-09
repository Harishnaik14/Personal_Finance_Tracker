from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from .models import Transaction
from .admin import TransactionAdmin

class TransactionAdminTest(TestCase):
    def test_search_fields(self):
        self.assertEqual(
            TransactionAdmin.search_fields,
            ('description', 'user__username', 'user__first_name', 'user__last_name')
        )
