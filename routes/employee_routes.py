from flask import Blueprint, render_template, request, redirect, url_for

employee_blueprint = Blueprint('employee', __name__)

employees = []

@employee_blueprint.route('/')
def home():
    return render_template('home.html')

@employee_blueprint.route('/employees')
def view_employees():
    return render_template('employees.html', employees=employees)

@employee_blueprint.route('/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        dept = request.form['department']
        salary = request.form['salary']
        emp_id = len(employees) + 1
        employees.append({'id': emp_id, 'name': name, 'department': dept, 'salary': salary})
        return redirect(url_for('employee.view_employees'))
    return render_template('add_employee.html')
