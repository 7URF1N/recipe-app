import functools
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g
from db import get_db

users_bp = Blueprint("users", __name__)

def login_required(view):
    @functools.wraps(view)
    def wrapped(**kwargs):
        if g.user is None:
            return redirect(url_for("users.login"))
        return view(**kwargs)
    return wrapped

@users_bp.before_app_request
def load_user():
    user_id = session.get("user_id")
    if user_id:
        g.user = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    else:
        g.user = None

@users_bp.route("/")
def index():
    return redirect(url_for("items.index"))

@users_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        db = get_db()
        error = None
        if not username:
            error = "Käyttäjänimi puuttuu."
        elif not password:
            error = "Salasana puuttuu."
        elif db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone():
            error = "Käyttäjänimi on jo käytössä."
        if error is None:
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            db.commit()
            flash("Tili luotu! Kirjaudu sisään.")
            return redirect(url_for("users.login"))
        flash(error)
    return render_template("register.html")

@users_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
        if user is None:
            flash("Väärä käyttäjänimi tai salasana.")
        else:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("items.index"))
    return render_template("login.html")

@users_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("users.login"))

@users_bp.route("/profile")
@login_required
def profile():
    db = get_db()
    recipes = db.execute("SELECT COUNT(*) FROM recipes WHERE user_id = ?", (g.user["id"],)).fetchone()[0]
    comments = db.execute("SELECT COUNT(*) FROM comments WHERE user_id = ?", (g.user["id"],)).fetchone()[0]
    return render_template("profile.html", recipe_count=recipes, comment_count=comments)