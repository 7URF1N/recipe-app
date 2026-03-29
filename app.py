from flask import Flask
from config import Config
from db import get_db, close_db

app = Flask(__name__)
app.config.from_object(Config)
app.teardown_appcontext(close_db)

from users import users_bp
from items import items_bp
app.register_blueprint(users_bp)
app.register_blueprint(items_bp)

@app.cli.command("init-db")
def init_db_command():
    db = get_db()
    with open("schema.sql", encoding="utf-8") as f:
        db.executescript(f.read())
    print("Tietokanta luotu.")

if __name__ == "__main__":
    app.run(debug=True)