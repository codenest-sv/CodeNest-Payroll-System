# utils/datastore.py
import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from reportlab.pdfgen import canvas
import csv

# -------------------------
# REAL DATA FILE LOCATION
# -------------------------
DATA_FILE = "data/admins.json"
BACKUP_FOLDER = "backups"

# -------------------------
# JSON I/O
# -------------------------
def read_json():
    if not os.path.exists(DATA_FILE):
        return {"admins": [], "employees": [], "payroll": []}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

            # ensure role present on older data
            for admin in data.get("admins", []):
                if "role" not in admin:
                    admin["role"] = "admin"

            return data
    except:
        return {"admins": [], "employees": [], "payroll": []}


def write_json(data):
    os.makedirs(os.path.dirname(DATA_FILE) or ".", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# -------------------------
# BACKUP
# -------------------------
def create_backup():
    if not os.path.exists(DATA_FILE):
        return False

    os.makedirs(BACKUP_FOLDER, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_FOLDER, f"backup_{timestamp}.json")

    with open(DATA_FILE, "r", encoding="utf-8") as src, open(backup_file, "w", encoding="utf-8") as dest:
        dest.write(src.read())

    return True


# -------------------------
# ADMINS
# -------------------------
def add_admin(username: str, password: str, role: str = "admin") -> bool:
    data = read_json()

    # prevent duplicate names
    for a in data.get("admins", []):
        if a.get("username") == username:
            return False

    hashed = generate_password_hash(password)

    # If first admin ever, promote to super_admin
    if len(data.get("admins", [])) == 0:
        role = "super_admin"

    data.setdefault("admins", []).append({
        "username": username,
        "password": hashed,
        "role": role
    })

    write_json(data)
    return True


def verify_admin(username: str, password: str) -> bool:
    data = read_json()
    for a in data.get("admins", []):
        if a.get("username") == username:
            return check_password_hash(a.get("password"), password)
    return False


def get_admin_by_username(username):
    data = read_json()
    for admin in data.get("admins", []):
        if admin.get("username") == username:
            return admin
    return None


def delete_admin(username) -> bool:
    """
    Remove admin by username.
    Returns True if removed, False otherwise (e.g. trying to delete last super_admin).
    """
    data = read_json()
    admins = data.get("admins", [])

    # prevent deleting non-existent
    found = next((a for a in admins if a.get("username") == username), None)
    if not found:
        return False

    # prevent removing last admin
    if len(admins) <= 1:
        return False

    admins = [a for a in admins if a.get("username") != username]
    data["admins"] = admins
    write_json(data)
    return True


# -------------------------
# EMPLOYEES
# -------------------------
def load_employees():
    return read_json().get("employees", [])


def save_employee(employee_dict):
    data = read_json()
    employees = data.get("employees", [])

    new_id = max([int(e.get("id", 0)) for e in employees], default=0) + 1
    employee_dict["id"] = new_id

    employees.append(employee_dict)
    data["employees"] = employees
    write_json(data)
    return True


def update_employee(updated):
    data = read_json()
    employees = data.get("employees", [])

    for i, e in enumerate(employees):
        if int(e.get("id")) == int(updated.get("id")):
            employees[i] = updated
            data["employees"] = employees
            write_json(data)
            return True

    return False


def delete_employee(employee_id):
    data = read_json()
    employees = data.get("employees", [])

    employees = [e for e in employees if int(e.get("id")) != int(employee_id)]
    data["employees"] = employees
    write_json(data)
    return True


# -------------------------
# PAYROLL
# -------------------------
def load_payroll_records():
    return read_json().get("payroll", [])


def has_been_paid_this_month(employee_id):
    data = read_json()
    records = data.get("payroll", [])

    now = datetime.utcnow()
    current_year = now.year
    current_month = now.month

    for r in records:
        try:
            if int(r.get("employee_id")) != int(employee_id):
                continue
        except:
            continue

        try:
            rd = datetime.fromisoformat(r.get("date")).date()
        except:
            continue

        if rd.year == current_year and rd.month == current_month:
            return True

    return False


def save_payroll_record(record):
    data = read_json()
    recs = data.get("payroll", [])

    new_id = max([int(r.get("id", 0)) for r in recs], default=0) + 1
    record["id"] = new_id

    recs.append(record)
    data["payroll"] = recs
    write_json(data)
    return True


# -------------------------
# EXPORTS (CSV / PDF)
# -------------------------
def export_payroll_pdf(record, output_path="exports/payslip.pdf"):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    import qrcode
    import os

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    logo_path = "assets/company_logo.png"
    if not os.path.exists("assets"):
        os.makedirs("assets")

    if not os.path.exists(logo_path):
        try:
            from PIL import Image, ImageDraw
            img = Image.new("RGB", (500, 150), "#0A3D62")
            d = ImageDraw.Draw(img)
            d.text((140, 50), "CodeNest Security Ltd.", fill="white")
            img.save(logo_path)
        except Exception:
            pass

    try:
        c.drawImage(logo_path, 40, height - 110, width=170, height=60, preserveAspectRatio=True)
    except Exception:
        pass

    c.setFont("Helvetica-Bold", 20)
    c.drawString(230, height - 80, "PAYSLIP")

    c.setFont("Helvetica", 10)
    c.drawString(230, height - 100, "Generated by CodeNest Payroll System")

    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.rect(40, height - 250, width - 80, 120)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 140, "Employee Information")

    c.setFont("Helvetica", 10)
    c.drawString(50, height - 160, f"Name: {record.get('employee_name', 'N/A')}")
    c.drawString(50, height - 180, f"Date: {record.get('date', 'N/A')}")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 220, "Salary Breakdown")

    c.setFont("Helvetica", 10)
    c.drawString(50, height - 240, f"Gross Salary:  ${record.get('gross_pay', 0):,.2f}")
    c.drawString(50, height - 260, f"Tax Deducted: ${record.get('tax', 0):,.2f}")
    c.drawString(50, height - 280, f"Net Salary:   ${record.get('net_pay', 0):,.2f}")

    qr_data = f"Employee: {record.get('employee_name')}\nNet Pay: ${record.get('net_pay')}"
    try:
        qr = qrcode.make(qr_data)
        qr_path = "assets/payslip_qr.png"
        qr.save(qr_path)
        c.drawImage(qr_path, width - 180, height - 260, width=120, height=120)
    except Exception:
        pass

    c.setLineWidth(1)
    c.line(50, 120, 250, 120)
    c.drawString(50, 105, "Authorized Signature")

    c.setFont("Helvetica-Oblique", 9)
    c.drawString(40, 50, "This is a system-generated payslip. No physical signature required.")

    c.save()

    return output_path


def export_payroll_csv(records, output_path="exports/payroll.csv"):
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    fieldnames = ["id", "employee_name", "date", "gross_pay", "tax", "net_pay"]

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for r in records:
            writer.writerow({
                "id": r.get("id"),
                "employee_name": r.get("employee_name"),
                "date": r.get("date"),
                "gross_pay": r.get("gross_pay"),
                "tax": r.get("tax"),
                "net_pay": r.get("net_pay"),
            })

    return output_path
