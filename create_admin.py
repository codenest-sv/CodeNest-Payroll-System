import json
from werkzeug.security import generate_password_hash

admin = {
    "username": "admin",
    "password": generate_password_hash("admin123")
}

with open("data/admins.json", "w") as f:
    json.dump([admin], f, indent=4)

print("Admin created successfully!")
