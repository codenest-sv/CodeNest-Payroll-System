# main_program_flow.py
# Author: Princeton Racca
# Description: Central control menu for the Employee Payroll System

from employee_crud import EmployeeCRUD
from payroll_logic import Payroll
from batch_processor import BatchProcessor
from report_generator import ReportGenerator

def main_menu():
    crud = EmployeeCRUD()
    payroll = Payroll()
    batch = BatchProcessor()
    report = ReportGenerator()

    while True:
        print("\n===== EMPLOYEE PAYROLL SYSTEM =====")
        print("1. Add Employee Record")
        print("2. View All Employees")
        print("3. Compute Payroll for an Employee")
        print("4. Run Monthly Batch Payroll")
        print("5. Generate Payroll Report")
        print("6. Delete Employee Record")
        print("7. Exit System")

        choice = input("Enter your choice (1-7): ")

        if choice == '1':
            crud.add_employee()
        elif choice == '2':
            crud.view_employees()
        elif choice == '3':
            payroll.compute_payroll()
        elif choice == '4':
            batch.run_batch()
        elif choice == '5':
            report.generate_report()
        elif choice == '6':
            crud.delete_employee()
        elif choice == '7':
            print("Exiting system... Goodbye, Manager 👋")
            break
        else:
            print("Invalid option! Please try again.")

if __name__ == "__main__":
    main_menu()
