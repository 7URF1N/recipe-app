import db

def get_all_classes():
    """Returns the database classifications in the format {title: [values]}."""
    sql = "SELECT title, value FROM classes ORDER BY id"
    rows = db.query(sql)
    classes = {}
    for row in rows:
        classes.setdefault(row["title"], []).append(row["value"])
    return classes

def add_recipe(name, ingredients, instructions, user_id, classes):
    sql = """INSERT INTO recipes (name, ingredients, instructions, user_id)
             VALUES (?, ?, ?, ?)"""
    db.execute(sql, [name, ingredients, instructions, user_id])
    recipe_id = db.last_insert_id()

    sql = "INSERT INTO recipe_classes (recipe_id, title, value) VALUES (?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [recipe_id, title, value])

    return recipe_id

def update_recipe(recipe_id, name, ingredients, instructions, classes):
    sql = """UPDATE recipes
             SET name = ?, ingredients = ?, instructions = ?
             WHERE id = ?"""
    db.execute(sql, [name, ingredients, instructions, recipe_id])

    db.execute("DELETE FROM recipe_classes WHERE recipe_id = ?", [recipe_id])
    sql = "INSERT INTO recipe_classes (recipe_id, title, value) VALUES (?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [recipe_id, title, value])

def remove_recipe(recipe_id):
    db.execute("DELETE FROM recipes WHERE id = ?", [recipe_id])

def get_recipe(recipe_id):
    sql = """SELECT r.id, r.name, r.ingredients, r.instructions,
                    r.created_at, r.user_id, u.username
             FROM recipes r, users u
             WHERE r.user_id = u.id AND r.id = ?"""
    result = db.query(sql, [recipe_id])
    return result[0] if result else None

def get_recipe_classes(recipe_id):
    sql = "SELECT title, value FROM recipe_classes WHERE recipe_id = ?"
    return db.query(sql, [recipe_id])

def get_all_recipes():
    sql = """SELECT r.id, r.name, r.created_at, r.user_id, u.username
             FROM recipes r, users u
             WHERE r.user_id = u.id
             ORDER BY r.id DESC"""
    return db.query(sql)

def find_recipes(query):
    sql = """SELECT r.id, r.name, r.created_at, r.user_id, u.username
             FROM recipes r, users u
             WHERE r.user_id = u.id
               AND (r.name LIKE ? OR r.ingredients LIKE ?)
             ORDER BY r.id DESC"""
    like = "%" + query + "%"
    return db.query(sql, [like, like])

def get_comments(recipe_id):
    sql = """SELECT c.id, c.content, c.stars, c.created_at,
                    c.user_id, u.username
             FROM comments c, users u
             WHERE c.user_id = u.id AND c.recipe_id = ?
             ORDER BY c.id DESC"""
    return db.query(sql, [recipe_id])

def add_comment(recipe_id, user_id, content, stars):
    sql = """INSERT INTO comments (recipe_id, user_id, content, stars)
             VALUES (?, ?, ?, ?)"""
    db.execute(sql, [recipe_id, user_id, content, stars])

def remove_comment(comment_id):
    db.execute("DELETE FROM comments WHERE id = ?", [comment_id])

def get_comment(comment_id):
    sql = "SELECT id, user_id, recipe_id FROM comments WHERE id = ?"
    result = db.query(sql, [comment_id])
    return result[0] if result else None

def get_stats():
    """Sovelluksen yleiset tilastot etusivulle."""
    total_recipes = db.query("SELECT COUNT(*) AS c FROM recipes")[0]["c"]
    total_users = db.query("SELECT COUNT(*) AS c FROM users")[0]["c"]
    total_comments = db.query("SELECT COUNT(*) AS c FROM comments")[0]["c"]
    return {
        "recipes": total_recipes,
        "users": total_users,
        "comments": total_comments,
    }