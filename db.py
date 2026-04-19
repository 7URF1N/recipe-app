import sqlite3
from flask import g

def get_connection():
    con = sqlite3.connect("database.db")
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con

def execute(sql, params=None):
    if params is None:
        params = []
    con = get_connection()
    try:
        result = con.execute(sql, params)
        con.commit()
        g.last_insert_id = result.lastrowid
    finally:
        con.close()

def last_insert_id():
    return g.get("last_insert_id", None)

def query(sql, params=None):
    if params is None:
        params = []
    con = get_connection()
    try:
        result = con.execute(sql, params).fetchall()
    finally:
        con.close()
    return result