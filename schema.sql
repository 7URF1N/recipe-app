CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE recipes (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users,
    name TEXT NOT NULL,
    ingredients TEXT NOT NULL,
    instructions TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE classes (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    value TEXT NOT NULL
);

CREATE TABLE recipe_classes (
    id INTEGER PRIMARY KEY,
    recipe_id INTEGER NOT NULL REFERENCES recipes ON DELETE CASCADE,
    title TEXT NOT NULL,
    value TEXT NOT NULL
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    recipe_id INTEGER NOT NULL REFERENCES recipes ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users,
    content TEXT NOT NULL,
    stars INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);