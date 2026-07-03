from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from auth_utils import hash_password
from database import get_db

auth = Blueprint('auth', __name__)

@auth.route("/login")
def login():
    if 'user_id' in session:
        return redirect(url_for('pages.dashboard'))
    return render_template("login.html")

@auth.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"success": False, "error": "Username and password required."})

    conn = get_db()
    existing = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
    if existing:
        conn.close()
        return jsonify({"success": False, "error": "Username already taken."})

    hashed = hash_password(password)
    conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
    conn.commit()

    user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    # Create user_stats row for new user with explicit starter values
    conn.execute(
        "INSERT OR IGNORE INTO user_stats (id, user_id, level, current_xp, total_xp, current_streak, longest_streak, last_activity_date) VALUES (?, ?, 1, 0, 0, 0, 0, NULL)",
        (user["id"], user["id"])
    )
    conn.commit()
    conn.close()

    session['user_id'] = user["id"]
    session['username'] = username
    return jsonify({"success": True, "username": username})

@auth.route("/login", methods=["POST"])
def do_login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")

    hashed = hash_password(password)
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed)).fetchone()
    conn.close()

    if not user:
        return jsonify({"success": False, "error": "Invalid username or password."})

    session['user_id'] = user["id"]
    session['username'] = user["username"]
    return jsonify({"success": True, "username": user["username"]})

@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
