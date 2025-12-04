# payroll_logic.py
import csv
import os

class Payroll:
    EMPLOYEE_FILE = os.path.join("data", "employee_records.csv")
    PAYROLL_FILE = os.path.join("data", "payroll_history.csv")

    def __init__(self):
        if not os.path.exists(self.PAYROLL_FILE):
            with open(self.PAYROLL_FILE, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["EmpID", "Name", "GrossPay", "Tax", "NetPay"])

    def compute_payroll(self):
        emp_id = input("Enter Employee ID to process payroll: ")
        with open(self.EMPLOYEE_FILE, mode='r') as file:
            reader = csv.DictReader(file)
            employee = None
            for row in reader:
                if row["EmpID"] == emp_id:
                    employee = row
                    break

        if not employee:
            print("❌ Employee not found!")
            return

        base_salary = float(employee["BaseSalary"])
        tax = base_salary * 0.05
        net_pay = base_salary - tax

        with open(self.PAYROLL_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([emp_id, employee["Name"], base_salary, tax, net_pay])

        print(f"✅ Payroll processed for {employee['Name']} - Net Pay: {net_pay}")
