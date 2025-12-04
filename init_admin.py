import json
import hashlib
import os

DATA_FILE = "database.json"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_admin():
    admin_username = "admin"
    admin_password = "admin123"
    hashed_pw = hash_password(admin_password)

    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
        except:
            data = {"admins": [], "employees": [], "payroll": []}
    else:
        data = {"admins": [], "employees": [], "payroll": []}

    # check if admin already exists
    for adm in data["admins"]:
        if adm["username"] == admin_username:
            print("Admin already exists.")
            return

    # create admin
    data["admins"].append({
        "username": admin_username,
        "password": hashed_pw
    })

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

    print("Admin created successfully!")
    print("Username: admin")
    print("Password: admin123")

if __name__ == "__main__":
    init_admin()
