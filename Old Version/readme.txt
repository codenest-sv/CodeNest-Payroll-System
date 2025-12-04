Employee Payroll Processing and Management System

Project Type: File-Based Payroll Management System
Programming Language: Python 3.13 (64-bit)
Developer: Princeton R. Zahnmie (Lead Programmer / Integrator)
Team Members: Jessica N. Younge
              J. Philip  Sleh
              Richard Trueh
Supervisor: Prof. Jeremiah 


📘 Project Overview
This system is a file-based application designed to manage employee payroll operations without using a database.
It handles employee registration, salary computation, tax deductions, batch processing, reporting, and data backup.


🧩 System Modules
1. main_program_flow.py       → Central program menu and integration controller.
2. employee_crud.py           → Handles add, update, delete, and search employee records.
3. payroll_logic.py           → Computes gross pay, tax, and net pay.
4. batch_processor.py         → Runs monthly batch payroll processing for all employees.
5. file_locking_manager.py    → Ensures data integrity, backups, and recovery.
6. report_generator.py        → Generates summary reports and pay slips.


📁 Folder Structure
src/         → Contains all Python source code modules.
data/        → Contains employee records, payroll history, and backups.
docs/        → Contains project documentation PDFs (SRS, Design, User Manual, etc.).
tests/       → Contains test scripts and test results.
reports/     → Contains generated payroll and performance reports.

⚙️ How to Run the Project
1. Open Terminal or Command Prompt in the project directory.
2. Run the main program:
       python src/main_program_flow.py
3. Follow the menu options to:
   - Add or view employee records
   - Process payroll (single or batch)
   - View and export reports
   - Exit the system safely


📦 Output Files
- data/employee_records.csv    → Stores employee details.
- data/payroll_history.csv     → Stores processed payroll data.
- reports/payroll_summary.pdf  → Stores generated payroll reports.
- data/backups/                → Stores backup archives.


✅ Project Goal
To demonstrate practical understanding of file organization and processing by
developing a payroll management system capable of efficient data handling,
backup, and reporting operations without relying on a database.
