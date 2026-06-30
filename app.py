from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from auth_utils import current_user_id, hash_password, login_required
from database import get_db, init_db
from nutrition_api import search_usda_foods

app = Flask(__name__)
app.secret_key = "habyx_secret_key_2026"

CATEGORIES = [
    {"name": "Workout",   "icon": "🏋️", "route": "workout"},
    {"name": "Cardio",    "icon": "🏃", "route": "cardio"},
    {"name": "Hydration", "icon": "💧", "route": "hydration"},
    {"name": "Hygiene",   "icon": "🪥", "route": "hygiene"},
    {"name": "Nutrition", "icon": "🥗", "route": "nutrition"},
]

# =========================================================
# AUTH PAGES
# =========================================================
@app.route("/login")
def login_page():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template("login.html")

@app.route("/register", methods=["POST"])
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

@app.route("/login", methods=["POST"])
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

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login_page'))

# =========================================================
# PAGES
# =========================================================
@app.route("/")
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))



@app.route("/activity")
@login_required
def home():
    un = session.get('username', 'User')
    initials = ''.join([w[0].upper() for w in un.split()[:2]])
    return render_template("activity.html", categories=CATEGORIES, username=un, initials=initials)

@app.route("/workout")
@login_required
def workout():
    un = session.get('username', 'User')
    initials = ''.join([w[0].upper() for w in un.split()[:2]])
    return render_template("workout.html", username=un, initials=initials)

@app.route("/cardio")
@login_required
def cardio():
    un = session.get('username', 'User')
    initials = ''.join([w[0].upper() for w in un.split()[:2]])
    return render_template("cardio.html", username=un, initials=initials)

@app.route("/hydration")
@login_required
def hydration():
    un = session.get('username', 'User')
    initials = ''.join([w[0].upper() for w in un.split()[:2]])
    return render_template("hydration.html", username=un, initials=initials)

@app.route("/hygiene")
@login_required
def hygiene():
    un = session.get('username', 'User')
    initials = ''.join([w[0].upper() for w in un.split()[:2]])
    return render_template("hygiene.html", username=un, initials=initials)

@app.route("/nutrition")
@login_required
def nutrition():
    un = session.get('username', 'User')
    initials = ''.join([w[0].upper() for w in un.split()[:2]])
    return render_template("nutrition.html", username=un, initials=initials)

@app.route("/dashboard")
@login_required
def dashboard():
    un = session.get('username', 'User')
    initials = ''.join([w[0].upper() for w in un.split()[:2]])
    return render_template("dashboard.html", username=un, initials=initials)

# =========================================================
# DASHBOARD FEED
# =========================================================
@app.route("/get-dashboard")
@login_required
def get_dashboard():
    uid = current_user_id()
    conn = get_db()
    c = conn.cursor()
    items = []

    try:
        c.execute("SELECT id, name, body_part FROM workouts WHERE user_id=? ORDER BY id DESC LIMIT 3", (uid,))
        for r in c.fetchall():
            items.append({"type": "Workout", "text": f"{r['name']} — {r['body_part']}", "id": r["id"]})
    except: pass

    try:
        c.execute("SELECT id, activity, duration FROM cardio WHERE user_id=? ORDER BY id DESC LIMIT 3", (uid,))
        for r in c.fetchall():
            items.append({"type": "Cardio", "text": f"{r['activity']} for {r['duration']} min", "id": r["id"]})
    except: pass

    try:
        c.execute("SELECT id, name, calories FROM meals WHERE user_id=? ORDER BY id DESC LIMIT 3", (uid,))
        for r in c.fetchall():
            items.append({"type": "Nutrition", "text": f"{r['name']} — {r['calories']} kcal", "id": r["id"]})
    except: pass

    try:
        c.execute("SELECT id, amount_ml, time FROM hydration WHERE user_id=? ORDER BY id DESC LIMIT 3", (uid,))
        for r in c.fetchall():
            items.append({"type": "Hydration", "text": f"{r['amount_ml']} ml at {r['time']}", "id": r["id"]})
    except: pass

    try:
        c.execute("SELECT id, task, time_of_day FROM hygiene WHERE user_id=? ORDER BY id DESC LIMIT 3", (uid,))
        for r in c.fetchall():
            items.append({"type": "Hygiene", "text": f"{r['task']} ({r['time_of_day']})", "id": r["id"]})
    except: pass

    conn.close()
    return jsonify(items)

# =========================================================
# DELETE ENDPOINTS
# =========================================================
@app.route("/delete-workout/<int:id>", methods=["DELETE"])
@login_required
def delete_workout(id):
    conn = get_db()
    conn.execute("DELETE FROM workouts WHERE id=? AND user_id=?", (id, current_user_id()))
    conn.commit(); conn.close()
    return jsonify({"status": "deleted"})

@app.route("/delete-cardio/<int:id>", methods=["DELETE"])
@login_required
def delete_cardio(id):
    conn = get_db()
    conn.execute("DELETE FROM cardio WHERE id=? AND user_id=?", (id, current_user_id()))
    conn.commit(); conn.close()
    return jsonify({"status": "deleted"})

@app.route("/delete-meal/<int:id>", methods=["DELETE"])
@login_required
def delete_meal(id):
    conn = get_db()
    conn.execute("DELETE FROM meals WHERE id=? AND user_id=?", (id, current_user_id()))
    conn.commit(); conn.close()
    return jsonify({"status": "deleted"})

@app.route("/delete-water/<int:id>", methods=["DELETE"])
@login_required
def delete_water(id):
    conn = get_db()
    conn.execute("DELETE FROM hydration WHERE id=? AND user_id=?", (id, current_user_id()))
    conn.commit(); conn.close()
    return jsonify({"status": "deleted"})

@app.route("/delete-hygiene/<int:id>", methods=["DELETE"])
@login_required
def delete_hygiene(id):
    conn = get_db()
    conn.execute("DELETE FROM hygiene WHERE id=? AND user_id=?", (id, current_user_id()))
    conn.commit(); conn.close()
    return jsonify({"status": "deleted"})

# =========================================================
# PLANNED TASKS
# =========================================================
@app.route("/save-planned-task", methods=["POST"])
@login_required
def save_planned_task():
    data = request.get_json()
    uid = current_user_id()
    conn = get_db()
    conn.execute("INSERT INTO planned_tasks (user_id, task_name, task_type, day_of_week, time, completed) VALUES (?,?,?,?,?,0)",
                 (uid, data["task_name"], data["task_type"], data["day"], data["time"]))
    conn.commit(); conn.close()
    return jsonify({"status": "saved"})

@app.route("/get-planned-tasks")
@login_required
def get_planned_tasks():
    uid = current_user_id()
    conn = get_db()
    rows = conn.execute("SELECT * FROM planned_tasks WHERE user_id=? ORDER BY day_of_week, time", (uid,)).fetchall()
    conn.close()
    return jsonify([{"id": r["id"], "task_name": r["task_name"], "task_type": r["task_type"],
                     "day": r["day_of_week"], "time": r["time"], "completed": r["completed"]} for r in rows])

@app.route("/toggle-planned-task/<int:id>", methods=["POST"])
@login_required
def toggle_planned_task(id):
    data = request.get_json()
    conn = get_db()
    conn.execute("UPDATE planned_tasks SET completed=?, date_completed=? WHERE id=? AND user_id=?",
                 (data["completed"], data.get("date_completed"), id, current_user_id()))
    conn.commit(); conn.close()
    return jsonify({"status": "updated"})

@app.route("/delete-planned-task/<int:id>", methods=["DELETE"])
@login_required
def delete_planned_task(id):
    conn = get_db()
    conn.execute("DELETE FROM planned_tasks WHERE id=? AND user_id=?", (id, current_user_id()))
    conn.commit(); conn.close()
    return jsonify({"status": "deleted"})

@app.route("/reset-week", methods=["POST"])
@login_required
def reset_week():
    try:
        conn = get_db()
        conn.execute("UPDATE planned_tasks SET completed=0, date_completed=NULL WHERE user_id=?", (current_user_id(),))
        conn.commit(); conn.close()
        return jsonify({"status": "reset"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =========================================================
# WORKOUT
# =========================================================
@app.route("/save-workout", methods=["POST"])
@login_required
def save_workout():
    data = request.get_json()
    conn = get_db()
    conn.execute("INSERT INTO workouts (user_id, name, body_part) VALUES (?,?,?)",
                 (current_user_id(), data["name"], data["body_part"]))
    conn.commit(); conn.close()
    return jsonify({"status": "saved"})

@app.route("/get-workouts")
@login_required
def get_workouts():
    conn = get_db()
    rows = conn.execute("SELECT * FROM workouts WHERE user_id=? ORDER BY id DESC", (current_user_id(),)).fetchall()
    conn.close()
    return jsonify([{"id": r["id"], "name": r["name"], "body_part": r["body_part"]} for r in rows])

# =========================================================
# CARDIO
# =========================================================
@app.route("/save-cardio", methods=["POST"])
@login_required
def save_cardio():
    data = request.get_json()
    conn = get_db()
    conn.execute("INSERT INTO cardio (user_id, activity, duration, intensity) VALUES (?,?,?,?)",
                 (current_user_id(), data["activity"], data["duration"], data["intensity"]))
    conn.commit(); conn.close()
    return jsonify({"status": "saved"})

# =========================================================
# HYDRATION
# =========================================================
@app.route("/save-water", methods=["POST"])
@login_required
def save_water():
    data = request.get_json()
    conn = get_db()
    conn.execute("INSERT INTO hydration (user_id, amount_ml) VALUES (?,?)",
                 (current_user_id(), data["amount_ml"]))
    conn.commit(); conn.close()
    return jsonify({"status": "saved"})

# =========================================================
# HYGIENE
# =========================================================
@app.route("/save-hygiene", methods=["POST"])
@login_required
def save_hygiene():
    data = request.get_json()
    conn = get_db()
    conn.execute("INSERT INTO hygiene (user_id, task, time_of_day) VALUES (?,?,?)",
                 (current_user_id(), data["task"], data["time_of_day"]))
    conn.commit(); conn.close()
    return jsonify({"status": "saved"})

# =========================================================
# NUTRITION
# =========================================================
@app.route("/save-meal", methods=["POST"])
@login_required
def save_meal():
    data = request.get_json()
    conn = get_db()
    conn.execute("INSERT INTO meals (user_id, name, meal_type, calories, protein, carbs, fat) VALUES (?,?,?,?,?,?,?)",
                 (current_user_id(), data["name"], data["meal_type"], data["calories"],
                  data.get("protein", 0), data.get("carbs", 0), data.get("fat", 0)))
    conn.commit(); conn.close()
    return jsonify({"status": "saved"})

@app.route("/get-meals/<meal_type>")
@login_required
def get_meals(meal_type):
    conn = get_db()
    rows = conn.execute("SELECT * FROM meals WHERE user_id=? AND meal_type=?", (current_user_id(), meal_type)).fetchall()
    conn.close()
    return jsonify([{"id": r["id"], "name": r["name"], "calories": r["calories"],
                     "protein": r["protein"], "carbs": r["carbs"], "fat": r["fat"]} for r in rows])

@app.route("/search-food", methods=["POST"])
def search_food():
    data = request.get_json()
    query = data.get("food", "")
    return jsonify({"foods": search_usda_foods(query)})

# =========================================================
# XP & USER STATS
# =========================================================
@app.route("/add-xp", methods=["POST"])
@login_required
def add_xp():
    data = request.get_json()
    xp = data.get("xp", 5)
    uid = current_user_id()
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO user_stats (id, user_id) VALUES (?,?)", (uid, uid))
    c.execute("UPDATE user_stats SET total_xp=total_xp+?, current_xp=current_xp+? WHERE user_id=?", (xp, xp, uid))
    conn.commit()
    stats = c.execute("SELECT total_xp FROM user_stats WHERE user_id=?", (uid,)).fetchone()
    conn.close()
    return jsonify({"total_xp": stats["total_xp"]})

@app.route("/get-user-stats")
@login_required
def get_user_stats():
    uid = current_user_id()
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO user_stats (id, user_id) VALUES (?,?)", (uid, uid))
    conn.commit()
    stats = c.execute("SELECT * FROM user_stats WHERE user_id=?", (uid,)).fetchone()
    conn.close()
    if stats:
        return jsonify({
            "level": stats["level"],
            "current_xp": stats["current_xp"],
            "total_xp": stats["total_xp"],
            "current_streak": stats["current_streak"],
            "longest_streak": stats["longest_streak"]
        })
    return jsonify({"error": "No stats found"})

@app.route("/get-username")
@login_required
def get_username():
    return jsonify({"username": session.get("username", "User")})

# =========================================================
# RUN
# =========================================================
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
