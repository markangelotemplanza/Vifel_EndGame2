from odoo import models
import datetime
from xlsxwriter.workbook import Workbook

class DailyInventoryXlsx(models.AbstractModel):
    _name = 'report.pallet_kilos_record_model.daily_inventory_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    @staticmethod
    def generate_header(sheet, sorted_lines, formats):
        sheet.write(0, 0, 'DAILY VIFEL INVENTORY', formats[0])
        sheet.write(1, 0, 'Warehouse: '+ sorted_lines[0].warehouse.name, formats[0]) 
        # Add table header
    @staticmethod
    def generateTableHeader(sheet, row_index, format):         
        tableHeaders = ['Date', 'Owner', 'Receiving Report No.', 'Withdrawal Report No.', 'Pallets Received', 'Pallets Withdrawn', 'Balance in Pallets', 'Kilos Received', 'Kilos Withdrawn', 'Balance in Kilos',]
        
        col_index = 0
        for headerText in tableHeaders:
            sheet.write(row_index, col_index, headerText, format)
            col_index +=1
     
    def generate_xlsx_report(self, workbook, data, lines):
        header_format = workbook.add_format({'font_size': 12, 'align': 'vcenter', 'bold': True, 'text_wrap': True})
        table_header_format = workbook.add_format({'font_size': 12, 'align': 'vcenter', 'bold': True, 'text_wrap': True, 'border': 1})
        normal_format = workbook.add_format({'font_size': 12, 'align': 'vcenter'})
        float_format = workbook.add_format({'font_size': 12, 'align': 'vcenter', 'num_format': '#,##0.00'})
        float_format_bold = workbook.add_format({'font_size': 12, 'align': 'vcenter', 'num_format': '#,##0.00', 'bold': True})
        date_format = workbook.add_format({'num_format': 'mm-dd-yyyy'})
        date_format2 = workbook.add_format({'num_format': 'MM-dd-yyyy'})

        
        
        sheet = workbook.add_worksheet('Pallet Kilos Record')
        sheet.set_column(0, 11, 21.5)
        row_index = 3 # Starting row index
        
        sorted_lines = sorted(lines, key=lambda x: x.create_date)
    
        self.generate_header(sheet, sorted_lines, [header_format, normal_format])
        self.generateTableHeader(sheet, row_index-2, table_header_format)
        sheet.write(row_index-1, 5, lines[0].total_balance_in_pallets + lines[0].pallets_withdrawn if 'WR' in lines[0].report_no else lines[0].total_balance_in_pallets - lines[0].pallets_received, float_format_bold)
        sheet.write(row_index-1, 8, lines[0].total_balance_in_kilos + lines[0].kilos_withdrawn if 'WR' in lines[0].report_no else lines[0].total_balance_in_kilos - lines[0].kilos_received, float_format_bold)

        summation = {'total_pallets_received': 0, 'total_pallets_withdrawn': 0, 'total_kilos_received': 0, 'total_kilos_withdrawn': 0}
        for line in sorted_lines:
            sheet.write(row_index, 0, line.create_date, date_format)
            sheet.write(row_index, 1, line.owner_id.name, normal_format)
            sheet.write(row_index, 2 if 'RR' in line.report_no else 3, line.report_no, normal_format)
            sheet.write(row_index, 4, line.pallets_received, float_format)
            sheet.write(row_index, 5, line.pallets_withdrawn, float_format)
            sheet.write(row_index, 6, line.overall_pallets, float_format)
            sheet.write(row_index, 7, line.kilos_received, float_format)
            sheet.write(row_index, 8, line.kilos_withdrawn, float_format)
            sheet.write(row_index, 9, line.overall_kilos, float_format)
            
            
            # Summing up various properties
            summation['total_pallets_received'] += line.pallets_received
            summation['total_pallets_withdrawn'] += line.pallets_withdrawn
            summation['total_kilos_received'] += line.kilos_received
            summation['total_kilos_withdrawn'] += line.kilos_withdrawn
            
            # Incrementing row index for the next line
            row_index += 1  
        # write summation total
        sheet.write(row_index, 4, summation['total_pallets_received'], float_format_bold)
        sheet.write(row_index, 5, summation['total_pallets_withdrawn'], float_format_bold)
        sheet.write(row_index, 7, summation['total_kilos_received'], float_format_bold)
        sheet.write(row_index, 8, summation['total_kilos_withdrawn'], float_format_bold)

        # sheet.write(row_index+3, 0, "GUARANTEED", header_format)



# import datetime

# def fill_missing_dates(arr):
#     """
#     Fills missing dates in an array of date-balance dictionaries and retains balance.

#     Args:
#         arr (list): A list of dictionaries with 'create_date' (string in YYYY-MM-DD HH:MM:SS format)
#                     and 'balance' keys.

#     Returns:
#         list: A new list with dictionaries for each date, including missing dates,
#               with balance carried forward from the last recorded date.
#     """

#     # Sort the array by create_date
#     sorted_lines = sorted(arr, key=lambda x: datetime.datetime.strptime(x['create_date'], '%Y-%m-%d %H:%M:%S').date())

#     # Get the start and end dates
#     start_date = datetime.datetime.strptime(sorted_lines[0]['create_date'], '%Y-%m-%d %H:%M:%S').date()
#     end_date = datetime.datetime.strptime(sorted_lines[-1]['create_date'], '%Y-%m-%d %H:%M:%S').date()

#     # Create an empty list to store the complete data
#     complete_data = []

#     # Loop through each day from start_date to end_date (inclusive)
#     current_date = start_date
#     previous_balance = None  # Keep track of the balance from the previous date
#     while current_date <= end_date:
#         # Check if a record exists for the current date
#         found_record = False
#         for item in sorted_lines:
#             if datetime.datetime.strptime(item['create_date'], '%Y-%m-%d %H:%M:%S').date() == current_date:
#                 # Record found, update complete_data and previous_balance
#                 complete_data.append({'create_date': item['create_date'], 'balance': item['balance']})
#                 previous_balance = item['balance']
#                 found_record = True
#                 break

#         # If no record found for the current date, use previous_balance
#         if not found_record:
#             if previous_balance is not None:
#                 # Create a datetime object with the current date and time from the previous date
#                 previous_date_with_time = datetime.datetime.strptime(current_date.strftime('%Y-%m-%d') + ' 00:00:00', '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=8)
#                 complete_data.append({'create_date': previous_date_with_time.strftime('%Y-%m-%d %H:%M:%S'), 'balance': previous_balance})
#             else:
#                 # Handle the case where there's no initial balance
#                 complete_data.append({'create_date': current_date.strftime('%Y-%m-%d %H:%M:%S'), 'balance': 0})

#         # Move to the next day
#         current_date += datetime.timedelta(days=1)

#     return complete_data

# # Example usage
# arr = [{'create_date': '2024-02-05 16:30:01', 'balance': 100}, {'create_date': '2024-02-15 16:30:01', 'balance': 200}, {'create_date': '2024-02-08 16:30:01', 'balance': 150}]

# complete_data = fill_missing_dates(arr)

# for x in complete_data:
#     print(x)


