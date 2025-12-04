# routes/admin_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file
from utils.datastore import (
    read_json,
    write_json,
    create_backup,
    load_employees,
    save_employee,
    delete_employee,
    export_payroll_csv,
    export_payroll_pdf,
    get_admin_by_username
)
from datetime import datetime, date

admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")

# ------------------------------------------------
# EMPLOYEE PROFILE VIEW
# ------------------------------------------------
@admin_blueprint.route("/employee/<int:id>")
def employee_profile(id):
    data = read_json()
    emp = next((e for e in data.get("employees", []) if int(e.get("id", 0)) == int(id)), None)
    payroll = [p for p in data.get("payroll", []) if int(p.get("employee_id", 0)) == int(id)]

    return render_template("employee_profile.html", emp=emp, payroll=payroll)


# ------------------------------------------------
# PAYROLL HISTORY PAGE
# ------------------------------------------------
@admin_blueprint.route("/payroll/history")
def payroll_history():
    if "admin" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    data = read_json()
    records = sorted(
        data.get("payroll", []),
        key=lambda r: r.get("date", ""),
        reverse=True
    )

    return render_template("payroll_history.html", records=records)


# ------------------------------------------------
# ROLE CHECK HELPERS
# ------------------------------------------------
def require_role(required):
    if "admin" not in session:
        return False

    admin = get_admin_by_username(session["admin"])
    if not admin:
        return False

    role = admin.get("role", "admin")

    if role == "super_admin":
        return True

    if required == "admin" and role in ["admin", "super_admin"]:
        return True

    if required == "viewer" and role in ["viewer", "admin", "super_admin"]:
        return True

    return False


def block_if_no(permission):
    if not require_role(permission):
        flash("You do not have permission to perform this action.", "danger")
        return redirect(url_for("admin.dashboard"))
    return None


# ------------------------------------------------
# DASHBOARD
# ------------------------------------------------
def _to_float(v):
    try:
        return float(v)
    except Exception:
        return 0.0


@admin_blueprint.route("/dashboard")
def dashboard():
    if "admin" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    data = read_json()
    employees = data.get("employees", [])
    payroll_records = data.get("payroll", [])
    admins = data.get("admins", [])

    total_employees = len(employees)
    total_payroll_records = len(payroll_records)
    num_admins = len(admins)

    avg_salary = 0.0
    if total_employees:
        avg_salary = sum(_to_float(e.get("salary", 0)) for e in employees) / total_employees

    total_gross = sum(_to_float(r.get("gross_pay", 0)) for r in payroll_records)
    total_net = sum(_to_float(r.get("net_pay", 0)) for r in payroll_records)
    total_tax = sum(_to_float(r.get("tax", 0)) for r in payroll_records)

    now = date.today()
    total_paid_this_month = 0.0

    for r in payroll_records:
        try:
            rd = datetime.fromisoformat(r.get("date")).date()
        except Exception:
            try:
                rd = datetime.strptime(r.get("date", ""), "%Y-%m-%d").date()
            except Exception:
                rd = None

        if rd and rd.year == now.year and rd.month == now.month:
            total_paid_this_month += _to_float(r.get("net_pay", 0))

    COMPANY_BUDGET = 2_000_000.0
    budget_remaining = max(0.0, COMPANY_BUDGET - total_net)

    recent_records = sorted(payroll_records, key=lambda r: r.get("date", ""), reverse=True)[:10]

    labels = []
    chart_values = []

    for i in range(5, -1, -1):
        y = now.year
        m = now.month - i
        while m <= 0:
            m += 12
            y -= 1
        labels.append(f"{y}-{m:02d}")

        total_m = 0.0
        for r in payroll_records:
            try:
                rd = datetime.fromisoformat(r.get("date")).date()
            except Exception:
                continue

            if rd.year == y and rd.month == m:
                total_m += _to_float(r.get("net_pay", 0))

        chart_values.append(round(total_m, 2))

    tally = {}
    for r in payroll_records:
        name = r.get("employee_name", "Unknown")
        tally[name] = tally.get(name, 0) + 1

    top_emps = sorted(tally.items(), key=lambda x: x[1], reverse=True)[:5]

    return render_template(
        "dashboard.html",
        total_employees=total_employees,
        total_payroll_records=total_payroll_records,
        total_paid_this_month=round(total_paid_this_month, 2),
        avg_salary=round(avg_salary, 2),
        total_gross=round(total_gross, 2),
        total_net=round(total_net, 2),
        total_tax=round(total_tax, 2),
        num_admins=num_admins,
        company_budget=COMPANY_BUDGET,
        budget_remaining=round(budget_remaining, 2),
        recent_records=recent_records,
        chart_labels=labels,
        chart_values=chart_values,
        top_emps=top_emps
    )


# ------------------------------------------------
# EMPLOYEE LIST PAGE (GET + POST add)
# ------------------------------------------------
@admin_blueprint.route("/employees", methods=["GET", "POST"])
def employees():
    if "admin" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        deny = block_if_no("admin")
        if deny:
            return deny

        name = (request.form.get("name") or "").strip()
        dept = (request.form.get("department") or "").strip()
        salary = request.form.get("salary", "0")

        try:
            salary = float(salary)
        except:
            salary = 0.0

        if not name:
            flash("Please enter employee name.", "warning")
        else:
            save_employee({"name": name, "department": dept, "salary": salary})
            flash("Employee added.", "success")
            return redirect(url_for("admin.employees"))

    employees = load_employees()
    return render_template("employees.html", employees=employees)


# ------------------------------------------------
# DELETE EMPLOYEE
# ------------------------------------------------
@admin_blueprint.route("/employee/delete/<int:emp_id>")
def delete_emp(emp_id):
    deny = block_if_no("admin")
    if deny:
        return deny

    delete_employee(emp_id)
    flash("Employee deleted.", "info")
    return redirect(url_for("admin.employees"))


# ------------------------------------------------
# EDIT EMPLOYEE
# ------------------------------------------------
@admin_blueprint.route("/employee/<int:id>/edit", methods=["GET", "POST"])
def edit_employee(id):
    data = read_json()
    emp = next((e for e in data.get("employees", []) if int(e.get("id", 0)) == int(id)), None)

    if not emp:
        flash("Employee not found.", "danger")
        return redirect(url_for("admin.employees"))

    if request.method == "POST":
        emp["name"] = request.form.get("name", emp.get("name"))
        emp["department"] = request.form.get("department", emp.get("department"))
        try:
            emp["salary"] = float(request.form.get("salary", emp.get("salary")))
        except:
            pass

        write_json(data)
        flash("Employee updated successfully!", "success")
        return redirect(url_for("admin.employee_profile", id=id))

    return render_template("edit_employee.html", emp=emp)


# ------------------------------------------------
# REGISTER ADMIN (ONLY SUPER ADMIN)
# ------------------------------------------------
@admin_blueprint.route("/register-admin", methods=["GET", "POST"])
def register_admin():
    deny = block_if_no("super_admin")
    if deny:
        return deny

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = (request.form.get("password") or "").strip()
        role = request.form.get("role") or "admin"

        if not username or not password:
            flash("Please fill all fields.", "warning")
        else:
            from utils.datastore import add_admin
            if add_admin(username, password, role):
                flash("New admin added.", "success")
                return redirect(url_for("admin.dashboard"))
            else:
                flash("Username exists.", "danger")

    return render_template("register_admin.html")


# ------------------------------------------------
# DELETE ADMIN (SUPER ADMIN ONLY)
# ------------------------------------------------
@admin_blueprint.route("/admin/delete/<username>")
def delete_admin_route(username):
    deny = block_if_no("super_admin")
    if deny:
        return deny

    from utils.datastore import delete_admin
    if delete_admin(username):
        flash("Admin deleted successfully.", "info")
    else:
        flash("Cannot delete this admin.", "danger")

    return redirect(url_for("admin.dashboard"))

# ------------------------------------------------
# PROCESS PAYROLL (updated salary-based + 5% tax)
# ------------------------------------------------
@admin_blueprint.route("/payroll/process", methods=["GET", "POST"])
def process_payroll():
    if "admin" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    data = read_json()
    employees = data.get("employees", [])

    if request.method == "POST":
        emp_id = int(request.form.get("employee_id"))
        days_worked = float(request.form.get("days_worked", 0))

        emp = next((e for e in employees if int(e["id"]) == emp_id), None)
        if not emp:
            flash("Employee not found.", "danger")
            return redirect(url_for("admin.process_payroll"))

        salary = float(emp.get("salary", 0))

        # NEW RULE:
        # net pay = (salary / 30 * days worked) - 5% tax
        daily_rate = salary / 30
        gross_pay = daily_rate * days_worked
        tax = gross_pay * 0.05
        net_pay = gross_pay - tax

        new_record = {
            "employee_id": emp_id,
            "employee_name": emp.get("name"),
            "days_worked": days_worked,
            "daily_rate": round(daily_rate, 2),
            "gross_pay": round(gross_pay, 2),
            "tax": round(tax, 2),
            "net_pay": round(net_pay, 2),
            "date": datetime.now().strftime("%Y-%m-%d")
        }

        data.setdefault("payroll", []).append(new_record)
        write_json(data)

        flash("Payroll processed successfully!", "success")
        return redirect(url_for("admin.payroll_history"))

    return render_template("process_payroll.html", employees=employees)

# ------------------------------------------------
# EXPORT CSV
# ------------------------------------------------
@admin_blueprint.route("/payroll/export/csv")
def payroll_export_csv():
    deny = block_if_no("admin")
    if deny:
        return deny

    data = read_json()
    records = data.get("payroll", [])

    csv_path = export_payroll_csv(records)
    return send_file(csv_path, as_attachment=True)


# ------------------------------------------------
# EXPORT PDF
# ------------------------------------------------
@admin_blueprint.route("/payroll/export/pdf")
def payroll_export_pdf():
    deny = block_if_no("admin")
    if deny:
        return deny

    data = read_json()
    records = data.get("payroll", [])

    if len(records) == 0:
        flash("No payroll records available for PDF export.", "warning")
        return redirect(url_for("admin.payroll_history"))

    last_record = records[-1]
    pdf_path = export_payroll_pdf(last_record)
    return send_file(pdf_path, as_attachment=True)
