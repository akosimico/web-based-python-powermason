from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom User Model
class User(AbstractUser):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
        ('Staff', 'Staff'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    # Add related_name to avoid conflict
    groups = models.ManyToManyField(
        'auth.Group', 
        related_name='custom_user_set',  # Custom related name for groups
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',  # Custom related name for user permissions
        blank=True
    )
# Project Model
class Project(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed'),
    ]
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_projects')

    def __str__(self):
        return self.name

# Cost Tracking Model
class Cost(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='costs')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_incurred = models.DateField()

    def __str__(self):
        return f"{self.project.name} - {self.description}"

# Project Estimation Model
class Estimation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='estimations')
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2)
    estimated_duration = models.PositiveIntegerField(help_text="Duration in days")
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Estimation for {self.project.name}"

# Report Model
class Report(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='reports')
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.project.name}: {self.title}"

# User Activity Log
class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"
