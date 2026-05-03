PAGE_SIZE = 20

import secrets
import sqlite3

from flask import (Flask, abort, flash, redirect,
                   render_template, request, session)

import config
import items
import users

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if "user_id" not in session:
        abort(403)

def check_csrf():
    if "csrf_token" not in session:
        abort(403)
    if request.form.get("csrf_token") != session["csrf_token"]:
        abort(403)

@app.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    if page < 1:
        page = 1
    total = items.count_all_recipes()
    page_count = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    if page > page_count:
        page = page_count
    all_recipes = items.get_all_recipes(page, PAGE_SIZE)
    stats = items.get_stats()
    return render_template("index.html", recipes=all_recipes, stats=stats,
                           page=page, page_count=page_count)

@app.route("/find")
def find():
    query = request.args.get("query", "").strip()
    page = request.args.get("page", 1, type=int)
    if page < 1:
        page = 1
    if query:
        total = items.count_find_recipes(query)
        page_count = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        if page > page_count:
            page = page_count
        results = items.find_recipes(query, page, PAGE_SIZE)
    else:
        results = []
        page_count = 1
    return render_template("find.html", query=query, results=results,
                           page=page, page_count=page_count)

@app.route("/recipe/<int:recipe_id>")
def show_recipe(recipe_id):
    recipe = items.get_recipe(recipe_id)
    if not recipe:
        abort(404)
    classes = items.get_recipe_classes(recipe_id)
    comments = items.get_comments(recipe_id)

    avg_stars = None
    if comments:
        avg_stars = round(sum(c["stars"] for c in comments) / len(comments), 2)

    return render_template(
        "show_recipe.html",
        recipe=recipe,
        classes=classes,
        comments=comments,
        avg_stars=avg_stars,
    )

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)
    page = request.args.get("page", 1, type=int)
    if page < 1:
        page = 1
    stats = users.get_user_stats(user_id)
    total = stats["recipes"]
    page_count = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    if page > page_count:
        page = page_count
    recipes = users.get_user_recipes(user_id, page, PAGE_SIZE)
    return render_template("show_user.html", user=user, recipes=recipes,
                           stats=stats, page=page, page_count=page_count)

@app.route("/new_recipe")
def new_recipe():
    require_login()
    all_classes = items.get_all_classes()
    return render_template("new_recipe.html", classes=all_classes)

@app.route("/create_recipe", methods=["POST"])
def create_recipe():
    require_login()
    check_csrf()

    name = request.form.get("name", "").strip()
    ingredients = request.form.get("ingredients", "").strip()
    instructions = request.form.get("instructions", "").strip()

    if not name or len(name) > 100:
        abort(403)
    if not ingredients or len(ingredients) > 5000:
        abort(403)
    if not instructions or len(instructions) > 10000:
        abort(403)

    all_classes = items.get_all_classes()
    chosen = []
    for title, values in all_classes.items():
        chosen_values = request.form.getlist("classes_" + title)
        for value in chosen_values:
            if value not in values:
                abort(403)
            chosen.append((title, value))

    recipe_id = items.add_recipe(
        name, ingredients, instructions, session["user_id"], chosen
    )
    return redirect("/recipe/" + str(recipe_id))

@app.route("/edit_recipe/<int:recipe_id>")
def edit_recipe(recipe_id):
    require_login()
    recipe = items.get_recipe(recipe_id)
    if not recipe:
        abort(404)
    if recipe["user_id"] != session["user_id"]:
        abort(403)

    all_classes = items.get_all_classes()
    selected = items.get_recipe_classes(recipe_id)
    selected_map = {}
    for row in selected:
        selected_map.setdefault(row["title"], []).append(row["value"])

    return render_template(
        "edit_recipe.html",
        recipe=recipe,
        classes=all_classes,
        selected=selected_map,
    )

@app.route("/update_recipe", methods=["POST"])
def update_recipe():
    require_login()
    check_csrf()

    recipe_id = int(request.form["recipe_id"])
    recipe = items.get_recipe(recipe_id)
    if not recipe:
        abort(404)
    if recipe["user_id"] != session["user_id"]:
        abort(403)

    name = request.form.get("name", "").strip()
    ingredients = request.form.get("ingredients", "").strip()
    instructions = request.form.get("instructions", "").strip()

    if not name or len(name) > 100:
        abort(403)
    if not ingredients or len(ingredients) > 5000:
        abort(403)
    if not instructions or len(instructions) > 10000:
        abort(403)

    all_classes = items.get_all_classes()
    chosen = []
    for title, values in all_classes.items():
        chosen_values = request.form.getlist("classes_" + title)
        for value in chosen_values:
            if value not in values:
                abort(403)
            chosen.append((title, value))

    items.update_recipe(recipe_id, name, ingredients, instructions, chosen)
    return redirect("/recipe/" + str(recipe_id))

@app.route("/remove_recipe/<int:recipe_id>", methods=["GET", "POST"])
def remove_recipe(recipe_id):
    require_login()
    recipe = items.get_recipe(recipe_id)
    if not recipe:
        abort(404)
    if recipe["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_recipe.html", recipe=recipe)

    check_csrf()
    if "remove" in request.form:
        items.remove_recipe(recipe_id)
        return redirect("/")
    return redirect("/recipe/" + str(recipe_id))

@app.route("/create_comment", methods=["POST"])
def create_comment():
    require_login()
    check_csrf()

    recipe_id = int(request.form["recipe_id"])
    recipe = items.get_recipe(recipe_id)
    if not recipe:
        abort(404)

    content = request.form.get("content", "").strip()
    stars_raw = request.form.get("stars", "")

    if not content or len(content) > 1000:
        abort(403)
    try:
        stars = int(stars_raw)
    except ValueError:
        abort(403)
    if stars < 1 or stars > 5:
        abort(403)

    items.add_comment(recipe_id, session["user_id"], content, stars)
    return redirect("/recipe/" + str(recipe_id))

@app.route("/remove_comment/<int:comment_id>", methods=["POST"])
def remove_comment(comment_id):
    require_login()
    check_csrf()

    comment = items.get_comment(comment_id)
    if not comment:
        abort(404)
    if comment["user_id"] != session["user_id"]:
        abort(403)

    recipe_id = comment["recipe_id"]
    items.remove_comment(comment_id)
    return redirect("/recipe/" + str(recipe_id))

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create_user", methods=["POST"])
def create_user():
    username = request.form.get("username", "").strip()
    password1 = request.form.get("password1", "")
    password2 = request.form.get("password2", "")

    if not username or len(username) > 20:
        flash("Username is missing or too long.")
        return redirect("/register")
    if not password1:
        flash("Password is missing.")
        return redirect("/register")
    if password1 != password2:
        flash("Passwords do not match.")
        return redirect("/register")

    try:
        users.create_user(username, password1)
    except sqlite3.IntegrityError:
        flash("Username is already taken.")
        return redirect("/register")

    flash("Account created successfully. You can now log in.")
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    user_id = users.check_login(username, password)
    if user_id:
        session["user_id"] = user_id
        session["username"] = username
        session["csrf_token"] = secrets.token_hex(16)
        return redirect("/")
    flash("Incorrect username or password.")
    return redirect("/login")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)