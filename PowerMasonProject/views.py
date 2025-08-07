from django.shortcuts import render, redirect
from django.http import HttpResponse
from openpyxl import load_workbook
from .models import Project  # Assuming you have a Project model
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, date
from django.contrib.auth.models import User  # Import User model
from django.contrib import messages  # Import the messages framework
from django.db import transaction  # Import transaction
from django.db import IntegrityError  # Import IntegrityError
from django.template.exceptions import TemplateDoesNotExist # Import this


def dashboard(request):
    return render(request, 'dashboard.html', {'active_tab': 'dashboard'})


def projects(request):
    projects = Project.objects.all()
    return render(request, 'projects.html', {'projects': projects, 'active_tab': 'projects'})


def costs(request):
    return render(request, 'costs.html', {'active_tab': 'costs'})


def estimation(request):
    return render(request, 'estimation.html', {'active_tab': 'estimation'})


def reports(request):
    return render(request, 'reports.html', {'active_tab': 'reports'})


def project_list(request):
    projects = Project.objects.all()  # Get all projects
    return render(request, 'projects.html', {'projects': projects})


def normalize_date_string(date_string):
    """
    Replace uncommon month abbreviations with standard ones.
    """
    replacements = {
        "SEPT": "SEP",
        "Sept": "SEP",  # Handle different cases
    }
    for old, new in replacements.items():
        date_string = date_string.replace(old, new)
    return date_string


def parse_date_string(date_str):
    """
    Helper function to parse date strings with flexible formats.
    """
    formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%m-%d-%Y",
        "%B %d, %Y",  # e.g., "July 24, 2023"
        "%b %d, %Y",  # e.g., "Jul 24, 2023"
        "%d %B %Y",  # e.g., 24 July 2023
        "%d %b %Y",  # e.g., 24 Jul 2023
        "%Y-%m-%d %H:%M:%S",  # Include time
        "%m/%d/%Y %H:%M:%S",
        "%d-%m-%Y %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%m-%d-%Y %H:%M:%S",
        "%B %d, %Y",
        "%b %d, %Y",
    ]
    date_str = normalize_date_string(date_str)  # Normalize the date string before parsing
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()  # Changed to datetime.strptime
        except ValueError:
            continue  # Try the next format
    raise ValueError(f"Date string '{date_str}' does not match any expected format.  Input was: '{date_str}'")


def safe_decimal(value):
    """
    Helper function to safely convert values to Decimal.
    Handles None, int, float, and existing Decimal values.
    """
    if value is None:
        return Decimal('0.00')
    if isinstance(value, (int, float)):
        return Decimal(str(value))  # Convert through string for precision
    if isinstance(value, Decimal):
        return value
    try:
        # Check if the value is a string and looks like a formula
        if isinstance(value, str) and ('+' in value or '-' in value or '*' in value or '/' in value):
            raise ValueError("Invalid value: Excel formula detected")
        return Decimal(str(value))
    except (TypeError, ValueError):
        return Decimal('0.00')  # Return 0.00 for unconvertible values
    except Exception as e:  # Catch other exceptions
        print(f"safe_decimal: Unexpected error converting value: {value}. Error: {e}, Value: {value}")
        return Decimal('0.00')


@transaction.atomic  # Wrap the entire process in a transaction
def import_excel(request):
    if request.method == "POST" and request.FILES.get("excel_file"):
        excel_file = request.FILES["excel_file"]

        try:
            workbook = load_workbook(excel_file)
            sheet = workbook.active

            # Extract values from the Excel sheet
            proj_id = sheet["B1"].value
            name = sheet["B2"].value
            location = sheet["B3"].value
            start_date_raw = sheet["B4"].value
            report_date_raw = sheet["H1"].value
            accomplished_to_date = safe_decimal(sheet["H2"].value)
            accomplished_before_period = safe_decimal(sheet["H3"].value)
            approved_contract = safe_decimal(sheet["E117"].value)

            # Get the progress report month and year from A6
            progress_report_month_year = sheet["A6"].value

            # Initialize total_expense here
            total_expense = Decimal('0.00')

            # Loop through the rows from 10 to 113 to calculate total expense
            for row in range(10, 114):  # Rows 10 to 113
                try:
                    # Get values for the formula F(row) / C(row) * E(row)
                    f_value = sheet[f"F{row}"].value
                    c_value = sheet[f"C{row}"].value
                    e_value = sheet[f"E{row}"].value

                    if f_value is not None and c_value is not None and e_value is not None:
                        # Safely convert the values to Decimal
                        f_value = safe_decimal(f_value)
                        c_value = safe_decimal(c_value)
                        e_value = safe_decimal(e_value)

                        if c_value != Decimal('0.00'):  # Avoid division by zero
                            total_expense += (f_value / c_value) * e_value
                except Exception as e:
                    print(f"Error calculating expense for row {row}: {e}")  # Log row errors
                    messages.error(request, f"Error calculating expense for row {row}.  Skipping row.")
                    # Don't pass, handle the error.
                    continue

            # Round off the total expense to 2 decimal places for saving in the model
            total_expense = total_expense.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

            # Validate required fields (including raw start date)
            if any(val is None for val in [proj_id, name, location, start_date_raw, report_date_raw]):
                error_message = "One or more required fields are missing."
                messages.error(request, error_message)
                raise ValueError(error_message)

            # Parse and validate start date
            start_date = None
            if isinstance(start_date_raw, str):
                start_date_raw = start_date_raw.strip()
                try:
                    start_date = parse_date_string(start_date_raw)
                except ValueError as e:
                    error_message = f"Invalid start date format: {e}"
                    messages.error(request, error_message)
                    raise ValueError(error_message)
            elif isinstance(start_date_raw, datetime):
                start_date = start_date_raw.date()
            elif isinstance(start_date_raw, date):
                start_date = start_date_raw
            else:
                error_message = "Unexpected type for start date."
                messages.error(request, error_message)
                raise ValueError(error_message)

            if start_date is None:
                error_message = "Failed to obtain a valid start date."
                messages.error(request, error_message)
                raise ValueError(error_message)

            # Parse report date
            report_date = None
            if report_date_raw:
                if isinstance(report_date_raw, str):
                    report_date_raw = report_date_raw.strip()
                    try:
                        report_date = parse_date_string(report_date_raw)
                    except ValueError as e:
                        error_message = f"Invalid report date format: {e}"
                        messages.error(request, error_message)
                        report_date = None  # important: set it to None, so the program does not crash.
                elif isinstance(report_date_raw, datetime):
                    report_date = report_date_raw.date()
                elif isinstance(report_date_raw, date):
                    report_date = report_date_raw

            # Calculate accomplished this period
            accomplished_this_period = total_expense / approved_contract * 100 if approved_contract else Decimal('0.00')
            accomplished_to_date = accomplished_this_period + accomplished_before_period

            # Get the current user (assuming user is logged in)
            user = request.user if request.user.is_authenticated else None

            # Call a function to handle the database operations
            return _process_project_data(request, proj_id, name, location, start_date, report_date, progress_report_month_year, accomplished_to_date, accomplished_before_period, accomplished_this_period, approved_contract, total_expense, user)

        except Exception as e:
            error_message = f"Error processing Excel file: {e}"
            messages.error(request, error_message)  # Use messages framework
            print(error_message)
            try:
                return render(request, 'import_excel.html', {'form': None, 'active_tab': 'import_excel'})  # Removed ExcelUploadForm()
            except TemplateDoesNotExist:
                return HttpResponse("Template 'import_excel.html' not found.", status=500)
    else:
        try:
            return render(request, 'import_excel.html', {'form': None, 'active_tab': 'import_excel'})  # Removed ExcelUploadForm()
        except TemplateDoesNotExist:
            return HttpResponse("Template 'import_excel.html' not found.", status=500)



def import_excel_form(request):
    try:
        return render(request, 'import_excel.html', {'form': None, 'active_tab': 'import_excel'})  # Removed ExcelUploadForm()
    except TemplateDoesNotExist:
        return HttpResponse("Template 'import_excel.html' not found.", status=500)



def _process_project_data(request, proj_id, name, location, start_date, report_date, progress_report_month_year, accomplished_to_date, accomplished_before_period, accomplished_this_period, approved_contract, total_expense, user):
    """
    Handles the creation or update of a Project record.
    This function is called from within the import_excel view.
    """
    try:
        project = Project.objects.create(
            proj_id=proj_id,
            name=name,
            location=location,
            start_date=start_date,
            report_date=report_date,
            progress_report_month_year=progress_report_month_year,
            accomplished_to_date=accomplished_to_date,
            accomplished_before_period=accomplished_before_period,
            accomplished_this_period=accomplished_this_period,
            approved_contract=approved_contract,
            total_expense=total_expense,
            created_by=user if user else None
        )
        messages.success(request, "Project data imported successfully.")
        return redirect("projects")
    except IntegrityError:
        # Handle the case where proj_id already exists.
        Project.objects.filter(proj_id=proj_id).update(
            name=name,
            location=location,
            start_date=start_date,
            report_date=report_date,
            progress_report_month_year=progress_report_month_year,
            accomplished_to_date=accomplished_to_date,
            accomplished_before_period=accomplished_before_period,
            accomplished_this_period=accomplished_this_period,
            approved_contract=approved_contract,
            total_expense=total_expense,
            created_by=user if user else None
        )
        messages.warning(request, "Project with this ID already exists.  Updated the existing project.")
        return redirect("projects")
