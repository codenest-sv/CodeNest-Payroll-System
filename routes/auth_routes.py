print("Loaded AUTH ROUTES from:", __file__)
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.datastore import read_json, add_admin, verify_admin, get_admin_by_username
from datetime import timedelta

auth_blueprint = Blueprint("auth", __name__, url_prefix="/auth")

SESSION_TIMEOUT_MINUTES = 45


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    data = read_json()  # Load admins from data/admins.json

    # -------------------------
    # FIRST-TIME SETUP (no admin saved)
    # -------------------------
    if len(data.get("admins", [])) == 0:
        flash("No admin found. Create your admin account now.", "info")

        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "").strip()

            if not username or not password:
                flash("Please enter a username and password.", "warning")
            else:
                # First admin = SUPER ADMIN
                add_admin(username, password, role="super_admin")
                session["admin"] = username
                session["role"] = "super_admin"
                flash("Super Admin account created successfully!", "success")
                return redirect(url_for("admin.dashboard"))

        return render_template("login.html", setup_mode=True)


    # -------------------------
    # NORMAL LOGIN
    # -------------------------
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if verify_admin(username, password):
            # Load role
            admin = get_admin_by_username(username)
            role = admin.get("role", "admin")

            session["admin"] = username
            session["role"] = role

            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for("admin.dashboard"))

        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html", setup_mode=False)


@auth_blueprint.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("auth.login"))

