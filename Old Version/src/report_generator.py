# report_generator.py
import csv
import os
import re
from backup_manager import BackupManager  # ✅ Added for automatic backup

class ReportGenerator:
    PAYROLL_FILE = os.path.join("data", "payroll_history.csv")

    def __init__(self):
        os.makedirs(os.path.dirname(self.PAYROLL_FILE), exist_ok=True)
        if not os.path.exists(self.PAYROLL_FILE):
            with open(self.PAYROLL_FILE, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["EmpID", "Name", "GrossPay", "Tax", "NetPay", "ProcessedDate"])

    def clean_number(self, value):
        """Convert strings like '$400 USD' safely to float"""
        if not value:
            return 0.0
        cleaned = re.sub(r'[^0-9.\-]', '', str(value))
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    def generate_report(self):
        print("\n--- Payroll Summary Report ---")

        if not os.path.exists(self.PAYROLL_FILE):
            print("❌ No payroll data found yet.")
            return

        total_gross = total_tax = total_net = 0.0
        record_count = 0

        with open(self.PAYROLL_FILE, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                gross = self.clean_number(row.get("GrossPay"))
                tax = self.clean_number(row.get("Tax"))
                net = self.clean_number(row.get("NetPay"))
                if gross > 0 or net > 0:
                    total_gross += gross
                    total_tax += tax
                    total_net += net
                    record_count += 1

        if record_count == 0:
            print("⚠️ No valid payroll records to summarize.")
            return

        print(f"Total Records: {record_count}")
        print(f"Total Gross Pay: {total_gross:.2f}")
        print(f"Total Tax Deducted: {total_tax:.2f}")
        print(f"Total Net Pay: {total_net:.2f}")
        print("✅ Report generated successfully!")

        # ✅ Automatic backup after report generation
        BackupManager().create_backup()
