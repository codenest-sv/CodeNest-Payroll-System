# batch_processor.py
import csv
import os
from datetime import datetime
from backup_manager import BackupManager  # ✅ Added for automatic backup

class BatchProcessor:
    EMP_FILE = os.path.join("data", "employee_records.csv")
    PAYROLL_FILE = os.path.join("data", "payroll_history.csv")

    def __init__(self):
        # ✅ Make sure payroll file exists with proper headers
        os.makedirs(os.path.dirname(self.PAYROLL_FILE), exist_ok=True)
        if not os.path.exists(self.PAYROLL_FILE):
            with open(self.PAYROLL_FILE, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["EmpID", "Name", "GrossPay", "Tax", "NetPay", "ProcessedDate"])

    def clean_salary(self, salary):
        """Remove symbols, spaces, or words so we can safely convert to float"""
        salary = str(salary)
        for symbol in ['$', 'USD', 'usd', 'L$', ' ']:
            salary = salary.replace(symbol, '')
        try:
            return float(salary)
        except ValueError:
            return 0.0  # fallback in case something invalid was entered

    def run_batch(self):
        print("\n⚙️ Running batch payroll for all employees...")

        if not os.path.exists(self.EMP_FILE):
            print("❌ Employee records not found. Please add employees first.")
            return

        with open(self.EMP_FILE, mode='r') as emp_file, open(self.PAYROLL_FILE, mode='a', newline='') as pay_file:
            reader = csv.DictReader(emp_file)
            writer = csv.writer(pay_file)

            for row in reader:
                gross = self.clean_salary(row["BaseSalary"])
                tax = gross * 0.05
                net = gross - tax
                date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                writer.writerow([row["EmpID"], row["Name"], gross, tax, net, date])

        # ✅ Automatic backup after batch payroll
        BackupManager().create_backup()

        print("✅ Batch payroll completed successfully!\nAll results saved in data/payroll_history.csv")
