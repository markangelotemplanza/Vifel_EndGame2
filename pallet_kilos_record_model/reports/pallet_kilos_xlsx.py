from odoo import models
import datetime
from xlsxwriter.workbook import Workbook

class PalletKilosXlsx(models.AbstractModel):
    _name = 'report.pallet_kilos_record_model.pallet_kilos_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    # Class variables to store format objects
    header_format = None
    table_header_format = None
    normal_format = None
    float_format = None
    float_format_bold = None
    date_format = None

    @classmethod
    def _define_formats(cls, workbook):
        """Define and assign format objects."""
        cls.header_format = workbook.add_format({'font_size': 12, 'align': 'vcenter', 'bold': True, 'text_wrap': True})
        cls.table_header_format = workbook.add_format({'font_size': 12, 'align': 'vcenter', 'bold': True, 'text_wrap': True, 'border': 1})
        cls.normal_format = workbook.add_format({'font_size': 12, 'align': 'vcenter'})
        cls.float_format = workbook.add_format({'font_size': 12, 'align': 'vcenter', 'num_format': '#,##0.00'})
        cls.float_format_bold = workbook.add_format({'font_size': 12, 'align': 'vcenter', 'num_format': '#,##0.00', 'bold': True})
        cls.date_format = workbook.add_format({'num_format': 'mm/dd/yy'})

    def generate_header(self, sheet, sorted_records):
        """Generate header section of the report."""
        sheet.write(0, 0, sorted_records[0].owner_id.name, self.header_format)
        sheet.write(1, 0, 'BILLING DETAILS-HOLDING', self.normal_format)
        start_date = sorted_records[0].create_date + datetime.timedelta(hours=8)
        end_date = sorted_records[-1].create_date + datetime.timedelta(hours=8)
        date_range = start_date.strftime('%B %d, %Y') + ' - ' + end_date.strftime('%B %d, %Y')
        sheet.write(2, 0, date_range)

    def generate_table_header(self, sheet, row_index):
        """Generate table header."""
        table_headers = ['Date', 'Receiving Report No.', 'Withdrawal Report No.', 'Pallets Received', 'Pallets Withdrawn', 'Balance in Pallets', 'Kilos Received', 'Kilos Withdrawn', 'Balance in Kilos', 'HOLDING RATE/day/pallet', 'HANDLING RATE']
        col_index = 0
        for header_text in table_headers:
            sheet.write(row_index, col_index, header_text, self.table_header_format)
            col_index += 1

    def generate_xlsx_report(self, workbook, data, records):
        """Generate the entire XLSX report."""
        # Ensure format objects are defined
        if not self.header_format:
            self._define_formats(workbook)
    
        # Group records by owner
        records_by_owner = {}
        for record in records:
            owner_name = record.owner_id.name
            if owner_name not in records_by_owner:
                records_by_owner[owner_name] = []
            records_by_owner[owner_name].append(record)
    
        # Iterate over each owner and generate a separate sheet
        for owner_name, owner_records in records_by_owner.items():
            # Create a new worksheet for the owner
            sheet = workbook.add_worksheet(owner_name)
            sheet.set_column(0, 11, 23)
            row_index = 5
    
            # Sort records by date
            sorted_records = sorted(owner_records, key=lambda x: x.create_date)
    
            # Generate header and table header
            self.generate_header(sheet, sorted_records)
            self.generate_table_header(sheet, row_index - 2)
    
            # Initialize summation dictionary
            summation = {'total_pallets_received': 0, 'total_pallets_withdrawn': 0, 'total_kilos_received': 0, 'total_kilos_withdrawn': 0}
    
            # Iterate over records and write data to the sheet
            for line in sorted_records:
                sheet.write(row_index, 0, line.create_date + datetime.timedelta(hours=8), self.date_format)
                sheet.write(row_index, 1 if 'RR' in line.report_no else 2, line.report_no, self.normal_format)
                sheet.write(row_index, 3, line.pallets_received, self.float_format)
                sheet.write(row_index, 4, line.pallets_withdrawn, self.float_format)
                sheet.write(row_index, 5, line.total_balance_in_pallets, self.float_format)
                sheet.write(row_index, 6, line.kilos_received, self.float_format)
                sheet.write(row_index, 7, line.kilos_withdrawn, self.float_format)
                sheet.write(row_index, 8, line.total_balance_in_kilos, self.float_format)
                sheet.write(row_index, 9, line.holding_rate, self.float_format)
                sheet.write(row_index, 10, line.handling_rate, self.float_format)
    
                # Sum up various properties
                summation['total_pallets_received'] += line.pallets_received
                summation['total_pallets_withdrawn'] += line.pallets_withdrawn
                summation['total_kilos_received'] += line.kilos_received
                summation['total_kilos_withdrawn'] += line.kilos_withdrawn
    
                # Increment row index
                row_index += 1
    
            # Write summation totals
            sheet.write(row_index, 3, summation['total_pallets_received'], self.float_format_bold)
            sheet.write(row_index, 4, summation['total_pallets_withdrawn'], self.float_format_bold)
            sheet.write(row_index, 6, summation['total_kilos_received'], self.float_format_bold)
            sheet.write(row_index, 7, summation['total_kilos_withdrawn'], self.float_format_bold)

            sheet.write(row_index+3, 0, "GUARANTEED", self.header_format)








