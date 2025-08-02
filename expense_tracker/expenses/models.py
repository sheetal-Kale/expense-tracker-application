from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('FOOD', 'Food'),
        ('TRANSPORT', 'Transport'),
        ('ENTERTAINMENT', 'Entertainment'),
        ('BILLS', 'Bills'),
        ('SHOPPING', 'Shopping'),
        ('OTHER', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category} - {self.amount}"
