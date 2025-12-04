# employee_crud.py
import csv
import os

class EmployeeCRUD:
    FILE_PATH = os.path.join("data", "employee_records.csv")

    def __init__(self):
        # ✅ Create file if it doesn't exist and add headers if missing
        os.makedirs(os.path.dirname(self.FILE_PATH), exist_ok=True)
        if not os.path.exists(self.FILE_PATH):
            with open(self.FILE_PATH, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["EmpID", "Name", "Department", "BaseSalary"])
        else:
            with open(self.FILE_PATH, mode='r+', newline='') as file:
                content = file.read().strip()
                if not content.startswith("EmpID"):
                    file.seek(0)
                    writer = csv.writer(file)
                    writer.writerow(["EmpID", "Name", "Department", "BaseSalary"])

    def add_employee(self):
        emp_id = input("Enter Employee ID: ").strip()
        name = input("Enter Employee Name: ").strip()
        dept = input("Enter Department: ").strip()
        salary = input("Enter Base Salary: ").strip()

        with open(self.FILE_PATH, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([emp_id, name, dept, salary])

        print(f"✅ Employee {name} added successfully!")

    def view_employees(self):
        print("\n--- Employee Records ---")
        if not os.path.exists(self.FILE_PATH):
            print("❌ No employee records found.")
            return

        with open(self.FILE_PATH, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                print(row)

    def delete_employee(self):
        emp_id = input("Enter Employee ID to delete: ").strip()
        temp_rows = []
        deleted = False

        with open(self.FILE_PATH, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["EmpID"] != emp_id:
                    temp_rows.append(row)
                else:
                    deleted = True

        with open(self.FILE_PATH, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["EmpID", "Name", "Department", "BaseSalary"])
            writer.writeheader()
            writer.writerows(temp_rows)

        if deleted:
            print(f"🗑️ Employee {emp_id} deleted successfully.")
        else:
            print("❌ Employee not found.")
