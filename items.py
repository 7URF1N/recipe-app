from flask import Blueprint, render_template, request, redirect, url_for, flash, g, abort
from db import get_db
from users import login_required

items_bp = Blueprint("items", __name__)
CATEGORIES = ["keitto", "pääruoka", "salaatti", "jälkiruoka", "juoma", "välipala", "muu"]

@items_bp.route("/recipes")
@login_required
def index():
    db = get_db()
    q = request.args.get("q", "")
    cat = request.args.get("category", "")
    sql = "SELECT r.*, u.username FROM recipes r JOIN users u ON r.user_id = u.id WHERE 1=1"
    params = []
    if q:
        sql += " AND (r.name LIKE ? OR r.ingredients LIKE ?)"
        params += [f"%{q}%", f"%{q}%"]
    if cat:
        sql += " AND r.category = ?"
        params.append(cat)
    recipes = db.execute(sql, params).fetchall()
    return render_template("index.html", recipes=recipes, categories=CATEGORIES, q=q, cat=cat)

@items_bp.route("/recipe/new", methods=["GET", "POST"])
@login_required
def new_recipe():
    if request.method == "POST":
        name = request.form["name"].strip()
        category = request.form["category"]
        ingredients = request.form["ingredients"].strip()
        instructions = request.form["instructions"].strip()
        if not name or not ingredients or not instructions:
            flash("Täytä kaikki kentät.")
        else:
            db = get_db()
            db.execute(
                "INSERT INTO recipes (name, category, ingredients, instructions, user_id) VALUES (?,?,?,?,?)",
                (name, category, ingredients, instructions, g.user["id"])
            )
            db.commit()
            return redirect(url_for("items.index"))
    return render_template("recipe_form.html", recipe=None, categories=CATEGORIES)

@items_bp.route("/recipe/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_recipe(id):
    db = get_db()
    recipe = db.execute("SELECT * FROM recipes WHERE id = ?", (id,)).fetchone()
    if recipe is None or recipe["user_id"] != g.user["id"]:
        abort(403)
    if request.method == "POST":
        name = request.form["name"].strip()
        category = request.form["category"]
        ingredients = request.form["ingredients"].strip()
        instructions = request.form["instructions"].strip()
        if not name or not ingredients or not instructions:
            flash("Täytä kaikki kentät.")
        else:
            db.execute(
                "UPDATE recipes SET name=?, category=?, ingredients=?, instructions=? WHERE id=?",
                (name, category, ingredients, instructions, id)
            )
            db.commit()
            return redirect(url_for("items.detail", id=id))
    return render_template("recipe_form.html", recipe=recipe, categories=CATEGORIES)

@items_bp.route("/recipe/<int:id>/delete", methods=["POST"])
@login_required
def delete_recipe(id):
    db = get_db()
    recipe = db.execute("SELECT * FROM recipes WHERE id = ?", (id,)).fetchone()
    if recipe is None or recipe["user_id"] != g.user["id"]:
        abort(403)
    db.execute("DELETE FROM recipes WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("items.index"))

@items_bp.route("/recipe/<int:id>")
@login_required
def detail(id):
    db = get_db()
    recipe = db.execute(
        "SELECT r.*, u.username FROM recipes r JOIN users u ON r.user_id = u.id WHERE r.id = ?", (id,)
    ).fetchone()
    if recipe is None:
        abort(404)
    comments = db.execute(
        "SELECT c.*, u.username FROM comments c JOIN users u ON c.user_id = u.id WHERE c.recipe_id = ? ORDER BY c.created_at DESC",
        (id,)
    ).fetchall()
    avg = db.execute("SELECT AVG(stars) FROM comments WHERE recipe_id = ?", (id,)).fetchone()[0]
    return render_template("detail.html", recipe=recipe, comments=comments, avg=round(avg,1) if avg else None)

@items_bp.route("/recipe/<int:id>/comment", methods=["POST"])
@login_required
def add_comment(id):
    stars = request.form.get("stars", type=int)
    content = request.form.get("content", "").strip()
    if not stars or stars < 1 or stars > 5:
        flash("Valitse tähtiarvio.")
        return redirect(url_for("items.detail", id=id))
    db = get_db()
    db.execute(
        "INSERT INTO comments (recipe_id, user_id, stars, content) VALUES (?,?,?,?)",
        (id, g.user["id"], stars, content)
    )
    db.commit()
    return redirect(url_for("items.detail", id=id))

@items_bp.route("/comment/<int:id>/delete", methods=["POST"])
@login_required
def delete_comment(id):
    db = get_db()
    comment = db.execute("SELECT * FROM comments WHERE id = ?", (id,)).fetchone()
    if comment is None or comment["user_id"] != g.user["id"]:
        abort(403)
    recipe_id = comment["recipe_id"]
    db.execute("DELETE FROM comments WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("items.detail", id=recipe_id))