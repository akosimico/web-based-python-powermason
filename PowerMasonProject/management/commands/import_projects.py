from openpyxl import load_workbook
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

# File path to your Excel file
excel_file = r"C:\Users\meejhay\Downloads\example_project_data.xlsx"

# Load the workbook and select the active sheet
workbook = load_workbook(excel_file)
sheet = workbook.active 

# Initialize a variable to store the sum
total_expense = Decimal('0.00')

# Define the number of decimal places to round to
decimal_places = 2

# Function to safely convert a value to Decimal
def safe_decimal(value):
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return Decimal('0.00')  # Default to 0.00 if conversion fails

# Loop through the rows from 10 to 113 (assuming you want this for each row)
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
                result = (f_value / c_value) * e_value
                # Round off the result to the specified decimal places
                total_expense += result
            else:
                print(f"Warning: Division by zero for row {row}, skipping this row.")
        else:
            print(f"Warning: Missing values in row {row}, skipping this row.")
    except Exception as e:
        print(f"Error in row {row}: {e}")

# Optionally, print the total expense rounded to 2 decimal places
total_expense = total_expense.quantize(Decimal('1.' + '0' * decimal_places), rounding=ROUND_HALF_UP)

# Retrieve and print values from the specified cells
try:
    proj_id = sheet["B1"].value  # Replace with actual cell reference for PROJ ID
    name = sheet["B2"].value  # Project name
    location = sheet["B3"].value  # Project location
    start_date = sheet["B4"].value  # Start date
    report_date = sheet["H1"].value  # Latest report date
    accomplished_to_date = sheet["H2"].value  # Accomplished to date
    accomplished_before_period = sheet["H3"].value  # Accomplished before period
    approved_contract = sheet["E117"].value  # Approved contract (budget)
    
    # Safely convert values to Decimal
    accomplished_before_period = safe_decimal(accomplished_before_period)
    accomplished_to_date = safe_decimal(accomplished_to_date)
    approved_contract = safe_decimal(approved_contract)

    print("Extracted Values:")
    print(f"PROJ ID: {proj_id}")
    print(f"Project: {name}")
    print(f"Location: {location}")
    print(f"Start Date: {start_date}")
    print(f"Report Date: {report_date}")
    print(f"Accomplished Before Period: {accomplished_before_period}")
    
    # Avoid division by zero if total_expense is 0
    if total_expense != Decimal('0.00') and approved_contract != Decimal('0.00'):
        # Calculate the percentage of Accomplished To This Period relative to approved contract
        accomplished_to_this_period_percentage = (total_expense / approved_contract) * Decimal('100')
        print(f"Accomplished To This Period (as a percentage of approved contract): {accomplished_to_this_period_percentage.quantize(Decimal('1.' + '0' * decimal_places), rounding=ROUND_HALF_UP):.2f}%")
    else:
        print("Cannot calculate percentage for Accomplished To This Period (either total expense or approved contract is zero).")
    
    # Calculate the total percentage of accomplished (Before and To Date)
    total_accomplished_percentage = (accomplished_before_period + accomplished_to_this_period_percentage) 

    # Round off the total accomplished percentage to the desired decimal places
    total_accomplished_percentage = total_accomplished_percentage.quantize(Decimal('1.' + '0' * decimal_places), rounding=ROUND_HALF_UP)

    print(f"Total Accomplished (Before + To Date) as a percentage of the approved contract: {total_accomplished_percentage:.2f}%")
    print(f"Approved Contract: {approved_contract}")
    print(f"Total Expense: {total_expense}")

except Exception as e:
    print(f"Error retrieving data: {e}")
