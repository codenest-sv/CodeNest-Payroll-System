# routes/payroll_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.datastore import (
    load_employees,
    save_payroll_record,
    load_payroll_records,
    create_backup,
    export_payroll_pdf,
    has_been_paid_this_month
)
from datetime import datetime

payroll_blueprint = Blueprint("payroll", __name__, url_prefix="/payroll")


@payroll_blueprint.route("/process", methods=["GET", "POST"])
def process_payroll():
    if "admin" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    employees = load_employees()

    if request.method == "POST":
        try:
            emp_id = int(request.form.get("employee") or 0)
        except:
            emp_id = 0
        try:
            days_worked = int(request.form.get("days_worked") or 0)
        except:
            days_worked = 0
        try:
            rate = float(request.form.get("rate") or 0)
        except:
            rate = 0.0

        emp = next((e for e in employees if int(e.get("id", 0)) == emp_id), None)
        if not emp:
            flash("Employee not found.", "danger")
            return redirect(url_for("payroll.process_payroll"))

        # Prevent paying same employee twice in 1 month
        if has_been_paid_this_month(emp_id):
            flash("This employee has already been paid this month.", "warning")
            return redirect(url_for("admin.payroll_history"))

        # Liberia uses UTC (Africa/Monrovia is UTC+0). Use UTC to avoid pytz dependency.
        today_date = datetime.utcnow().date().isoformat()

        gross = rate * days_worked
        tax = gross * 0.05
        net = gross - tax

        record = {
            "employee_id": emp_id,
            "employee_name": emp.get("name"),
            "days_worked": days_worked,
            "rate": rate,
            "gross_pay": round(gross, 2),
            "tax": round(tax, 2),
            "net_pay": round(net, 2),
            "date": today_date
        }

        save_payroll_record(record)

        # Generate payslip PDF
        try:
            export_payroll_pdf(record)
            flash("Payslip generated successfully!", "success")
        except Exception as e:
            flash(f"PDF generation error: {e}", "danger")

        create_backup()
        return redirect(url_for("admin.payroll_history"))

    return render_template("process_payroll.html", employees=employees)
