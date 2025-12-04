from flask import Flask, redirect, url_for, session
from datetime import timedelta

from routes.auth_routes import auth_blueprint
from routes.admin_routes import admin_blueprint
from routes.payroll_routes import payroll_blueprint

app = Flask(__name__)
app.secret_key = "supersecretkey123"

# Session config
app.permanent_session_lifetime = timedelta(minutes=45)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Blueprints
app.register_blueprint(auth_blueprint)
app.register_blueprint(admin_blueprint)
app.register_blueprint(payroll_blueprint)

@app.route("/")
def home():
    if session.get("admin"):
        return redirect(url_for("admin.dashboard"))
    return redirect(url_for("auth.login"))

if __name__ == "__main__":
    app.run(debug=True)
