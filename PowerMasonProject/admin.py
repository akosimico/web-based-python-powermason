from django.contrib import admin
from .models import Project

class ProjectAdmin(admin.ModelAdmin):
    # Fields to display in the admin list view
    list_display = (
        "proj_id",
        "name",
        "location",
        "start_date",
        "report_date",
        "progress_report_month_year",  # Add progress_report_month_year here
        "accomplished_to_date",
        "accomplished_before_period",
        "accomplished_this_period",
        "approved_contract",
        "total_expense"
    )

    # Fields to filter by in the admin interface
    list_filter = ("start_date", "report_date", "location", "progress_report_month_year") # Add to filters

    # Fields to search by in the admin interface
    search_fields = ("proj_id", "name", "location", "progress_report_month_year") # Add to search fields

    # Fields to display in the detail view when editing a Project
    fieldsets = (
        ("Project Details", {
            "fields": (
                "proj_id",
                "name",
                "location",
                "start_date",
                "report_date",
                "progress_report_month_year", # Add here as well
            )
        }),
        ("Financial Details", {
            "fields": (
                "accomplished_to_date",
                "accomplished_before_period",
                "accomplished_this_period",
                "approved_contract",
                "total_expense"
            )
        }),
    )

# Register your Project model with the ProjectAdmin configuration
admin.site.register(Project, ProjectAdmin)