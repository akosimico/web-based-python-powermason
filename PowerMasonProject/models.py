from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.contrib.auth.models import User

# Project Model
class Project(models.Model):
    STATUS_CHOICES = [
        ('onTrack', 'onTrack'),
        ('Delayed', 'Delayed'),
        ('Completed', 'Completed'),
    ]

    # Fields
    proj_id = models.CharField(max_length=50, unique=True)  # Unique Project ID
    name = models.CharField(max_length=255)  # Project Name
    location = models.CharField(max_length=255, blank=True, null=True)  # Project Location
    start_date = models.DateField()  # Start Date
    end_date = models.DateField(blank=True, null=True)
    report_date = models.DateField(blank=True, null=True)  # Latest Report Date
    progress_report_month_year = models.CharField(max_length=50, blank=True, null=True) # Progress Report Month and Year
    accomplished_to_date = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    accomplished_before_period = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    accomplished_this_period = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    approved_contract = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00'),  # VAT Inclusive (Budget)
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    total_expense = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00'),  # Sum of Expense column
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    # Metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='onTrack')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_projects')
    
    def __str__(self):
        return f"{self.proj_id} - {self.name}"