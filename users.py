from werkzeug.security import check_password_hash, generate_password_hash
import db

def get_user(user_id):
    sql = "SELECT id, username FROM users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0] if result else None

def get_user_by_username(username):
    sql = "SELECT id, username, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])
    return result[0] if result else None

def create_user(username, password):
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    db.execute(sql, [username, password_hash])

def check_login(username, password):
    user = get_user_by_username(username)
    if not user:
        return None
    if check_password_hash(user["password_hash"], password):
        return user["id"]
    return None

def get_user_recipes(user_id):
    sql = """SELECT id, name, created_at
             FROM recipes
             WHERE user_id = ?
             ORDER BY id DESC"""
    return db.query(sql, [user_id])

def get_user_stats(user_id):
    recipe_count = db.query(
        "SELECT COUNT(*) AS c FROM recipes WHERE user_id = ?", [user_id]
    )[0]["c"]

    comment_count = db.query(
        "SELECT COUNT(*) AS c FROM comments WHERE user_id = ?", [user_id]
    )[0]["c"]

    received_comments = db.query(
        """SELECT COUNT(*) AS c
           FROM comments c, recipes r
           WHERE c.recipe_id = r.id AND r.user_id = ?""",
        [user_id],
    )[0]["c"]

    avg_row = db.query(
        """SELECT AVG(c.stars) AS avg
           FROM comments c, recipes r
           WHERE c.recipe_id = r.id AND r.user_id = ?""",
        [user_id],
    )[0]
    avg_stars = round(avg_row["avg"], 2) if avg_row["avg"] else None

    return {
        "recipes": recipe_count,
        "comments_given": comment_count,
        "comments_received": received_comments,
        "avg_stars": avg_stars,
    }