from flask import Flask, render_template, request, jsonify
import requests
import os
import sqlite3

app = Flask(__name__)

# =========================================================
# CATEGORIES (single source of truth)
# =========================================================
CATEGORIES = [
    {"name": "Workout",   "icon": "🏋️", "route": "workout"},
    {"name": "Cardio",    "icon": "🏃", "route": "cardio"},
    {"name": "Hydration", "icon": "💧", "route": "hydration"},
    {"name": "Hygiene",   "icon": "🪥", "route": "hygiene"},
    {"name": "Nutrition", "icon": "🥗", "route": "nutrition"},
]

# =========================================================
# DATABASE
# =========================================================
def get_db():
    conn = sqlite3.connect("fitness.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        body_part TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS cardio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        activity TEXT,
        duration INTEGER,
        intensity TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS meals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        meal_type TEXT,
        calories INTEGER,
        protein REAL,
        carbs REAL,
        fat REAL
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS hydration (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount_ml INTEGER,
        time TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS hygiene (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT,
        time_of_day TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS planned_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_name TEXT,
        task_type TEXT,
        day_of_week INTEGER,
        time TEXT,
        completed BOOLEAN DEFAULT 0,
        date_completed TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS user_stats (
        id INTEGER PRIMARY KEY,
        level INTEGER DEFAULT 1,
        current_xp INTEGER DEFAULT 0,
        total_xp INTEGER DEFAULT 0,
        current_streak INTEGER DEFAULT 0,
        longest_streak INTEGER DEFAULT 0,
        last_activity_date TEXT
    )""")

    c.execute("INSERT OR IGNORE INTO user_stats (id) VALUES (1)")

    conn.commit()
    conn.close()


# =========================================================
# PAGES
# =========================================================
@app.route("/")
@app.route("/activity")
def home():
    return render_template("activity.html", categories=CATEGORIES)

@app.route("/workout")
def workout():
    return render_template("workout.html")

@app.route("/cardio")
def cardio():
    return render_template("cardio.html")

@app.route("/hydration")
def hydration():
    return render_template("hydration.html")

@app.route("/hygiene")
def hygiene():
    return render_template("hygiene.html")

@app.route("/nutrition")
def nutrition():
    return render_template("nutrition.html")


# =========================================================
# DASHBOARD FEED
# =========================================================
@app.route("/get-dashboard")
def get_dashboard():
    conn = get_db()
    c = conn.cursor()
    items = []

    try:
        c.execute("SELECT id, name, body_part FROM workouts ORDER BY id DESC LIMIT 3")
        for r in c.fetchall():
            items.append({"type": "Workout", "text": f"{r['name']} — {r['body_part']}", "id": r["id"]})
    except: pass

    try:
        c.execute("SELECT id, activity, duration FROM cardio ORDER BY id DESC LIMIT 3")
        for r in c.fetchall():
            items.append({"type": "Cardio", "text": f"{r['activity']} for {r['duration']} min", "id": r["id"]})
    except: pass

    try:
        c.execute("SELECT id, name, calories FROM meals ORDER BY id DESC LIMIT 3")
        for r in c.fetchall():
            items.append({"type": "Nutrition", "text": f"{r['name']} — {r['calories']} kcal", "id": r["id"]})
    except: pass

    try:
        c.execute("SELECT id, amount_ml, time FROM hydration ORDER BY id DESC LIMIT 3")
        for r in c.fetchall():
            items.append({"type": "Hydration", "text": f"{r['amount_ml']} ml at {r['time']}", "id": r["id"]})
    except: pass

    try:
        c.execute("SELECT id, task, time_of_day FROM hygiene ORDER BY id DESC LIMIT 3")
        for r in c.fetchall():
            items.append({"type": "Hygiene", "text": f"{r['task']} ({r['time_of_day']})", "id": r["id"]})
    except: pass

    conn.close()
    return jsonify(items)


# =========================================================
# DELETE ENDPOINTS
# =========================================================
@app.route("/delete-workout/<int:id>", methods=["DELETE"])
def delete_workout(id):
    conn = get_db()
    conn.execute("DELETE FROM workouts WHERE id=?", (id,))
    conn.commit(); conn.close()
    return jsonify({"status": "deleted"})

@app.route("/delete-cardio/<int:id>", methods=["DELETE"])
def delete_cardio(id):
    conn = get_db()
    conn.execute("DELETE FROM cardio WHERE id=?", (id,))
    conn.commit(); conn.close()
    return jsonify({"status": "deleted"})

@app.route("/delete-meal/<int:id>", methods=["DELETE"])
def delete_meal(id):
    conn = get_db()
    conn.execute("DELETE FROM meals WHERE id=?", (id,))
    conn.commit(); conn.close()
    return jsonify({"status": "deleted"})

@app.route("/delete-water/<int:id>", methods=["DELETE"])
def delete_water(id):
    conn = get_db()
    conn.execute("DELETE FROM hydration WHERE id=?", (id,))
    conn.commit(); conn.close()
    return jsonify({"status": "deleted"})

@app.route("/delete-hygiene/<int:id>", methods=["DELETE"])
def delete_hygiene(id):
    conn = get_db()
    conn.execute("DELETE FROM hygiene WHERE id=?", (id,))
    conn.commit(); conn.close()
    return jsonify({"status": "deleted"})


# =========================================================
# PLANNED TASKS (Weekly Planner)
# =========================================================
@app.route("/save-planned-task", methods=["POST"])
def save_planned_task():
    data = request.get_json()
    conn = get_db()
    conn.execute("""INSERT INTO planned_tasks (task_name, task_type, day_of_week, time, completed)
                    VALUES (?, ?, ?, ?, 0)""",
                 (data["task_name"], data["task_type"], data["day"], data["time"]))
    conn.commit(); conn.close()
    return jsonify({"status": "saved"})

@app.route("/get-planned-tasks")
def get_planned_tasks():
    conn = get_db()
    rows = conn.execute("SELECT * FROM planned_tasks ORDER BY day_of_week, time").fetchall()
    conn.close()
    return jsonify([{"id": r["id"], "task_name": r["task_name"], "task_type": r["task_type"],
                     "day": r["day_of_week"], "time": r["time"], "completed": r["completed"]} for r in rows])

@app.route("/toggle-planned-task/<int:id>", methods=["POST"])
def toggle_planned_task(id):
    data = request.get_json()
    conn = get_db()
    conn.execute("UPDATE planned_tasks SET completed=?, date_completed=? WHERE id=?",
                 (data["completed"], data["date_completed"] if data["completed"] else None, id))
    conn.commit(); conn.close()
    return jsonify({"status": "updated"})

@app.route("/delete-planned-task/<int:id>", methods=["DELETE"])
def delete_planned_task(id):
    conn = get_db()
    conn.execute("DELETE FROM planned_tasks WHERE id=?", (id,))
    conn.commit(); conn.close()
    return jsonify({"status": "deleted"})

@app.route("/reset-week", methods=["POST"])
def reset_week():
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("UPDATE planned_tasks SET completed = 0, date_completed = NULL")
        conn.commit()
        conn.close()
        return jsonify({"status": "reset"})
    except Exception as e:
        print(f"ERROR in reset_week: {e}")
        return jsonify({"error": str(e)}), 500


# =========================================================
# WORKOUT
# =========================================================
@app.route("/save-workout", methods=["POST"])
def save_workout():
    data = request.get_json()
    conn = get_db()
    conn.execute("INSERT INTO workouts (name, body_part) VALUES (?, ?)",
                 (data["name"], data["body_part"]))
    conn.commit(); conn.close()
    return jsonify({"status": "saved"})

@app.route("/get-workouts")
def get_workouts():
    conn = get_db()
    rows = conn.execute("SELECT * FROM workouts ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([{"id": r["id"], "name": r["name"], "body_part": r["body_part"]} for r in rows])


# =========================================================
# CARDIO
# =========================================================
@app.route("/save-cardio", methods=["POST"])
def save_cardio():
    data = request.get_json()
    conn = get_db()
    conn.execute("INSERT INTO cardio (activity, duration, intensity) VALUES (?, ?, ?)",
                 (data["activity"], data["duration"], data["intensity"]))
    conn.commit(); conn.close()
    return jsonify({"status": "saved"})

@app.route("/get-cardio")
def get_cardio():
    conn = get_db()
    rows = conn.execute("SELECT * FROM cardio ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([{"id": r["id"], "activity": r["activity"],
                     "duration": r["duration"], "intensity": r["intensity"]} for r in rows])


# =========================================================
# HYDRATION
# =========================================================
@app.route("/save-water", methods=["POST"])
def save_water():
    data = request.get_json()
    conn = get_db()
    conn.execute("INSERT INTO hydration (amount_ml) VALUES (?)", (data["amount_ml"],))
    conn.commit(); conn.close()
    return jsonify({"status": "saved"})

@app.route("/get-water")
def get_water():
    conn = get_db()
    rows = conn.execute("SELECT * FROM hydration ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([{"id": r["id"], "amount_ml": r["amount_ml"], "time": r["time"]} for r in rows])


# =========================================================
# HYGIENE
# =========================================================
@app.route("/save-hygiene", methods=["POST"])
def save_hygiene():
    data = request.get_json()
    conn = get_db()
    conn.execute("INSERT INTO hygiene (task, time_of_day) VALUES (?, ?)",
                 (data["task"], data["time_of_day"]))
    conn.commit(); conn.close()
    return jsonify({"status": "saved"})

@app.route("/get-hygiene")
def get_hygiene():
    conn = get_db()
    rows = conn.execute("SELECT * FROM hygiene ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([{"id": r["id"], "task": r["task"], "time_of_day": r["time_of_day"]} for r in rows])


# =========================================================
# NUTRITION
# =========================================================
@app.route("/save-meal", methods=["POST"])
def save_meal():
    data = request.get_json()
    conn = get_db()
    conn.execute("""INSERT INTO meals (name, meal_type, calories, protein, carbs, fat)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                 (data["name"], data["meal_type"], data["calories"],
                  data.get("protein", 0), data.get("carbs", 0), data.get("fat", 0)))
    conn.commit(); conn.close()
    return jsonify({"status": "saved"})

@app.route("/get-meals/<meal_type>")
def get_meals(meal_type):
    conn = get_db()
    rows = conn.execute("SELECT * FROM meals WHERE meal_type=?", (meal_type,)).fetchall()
    conn.close()
    return jsonify([{"id": r["id"], "name": r["name"], "calories": r["calories"],
                     "protein": r["protein"], "carbs": r["carbs"], "fat": r["fat"]} for r in rows])

@app.route("/search-food", methods=["POST"])
def search_food():
    data = request.get_json()
    query = data.get("food", "")
    api_key = os.getenv("USDA_API_KEY", "kMAwFEYVrEHWy7gxddjpZe0VoWe1i1CDtdDg2KdD")
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {"query": query, "pageSize": 8, "api_key": api_key}

    try:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            return jsonify({"foods": []})
        result = response.json()
        foods = []
        for food in result.get("foods", []):
            calories = protein = carbs = fat = 0
            for nutrient in food.get("foodNutrients", []):
                name = nutrient.get("nutrientName", "").lower()
                value = nutrient.get("value", 0)
                if "energy" in name:          calories = value
                elif "protein" in name:       protein  = value
                elif "carbohydrate" in name:  carbs    = value
                elif "fat" in name:           fat      = value
            foods.append({"name": food.get("description", "Unknown Food"),
                          "calories": calories, "protein": protein,
                          "carbs": carbs, "fat": fat})
        return jsonify({"foods": foods})
    except Exception as e:
        print("ERROR:", e)
        return jsonify({"foods": []})


# =========================================================
# XP & USER STATS
# =========================================================
@app.route("/add-xp", methods=["POST"])
def add_xp():
    data = request.get_json()
    xp = data.get("xp", 5)
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE user_stats SET total_xp = total_xp + ?, current_xp = current_xp + ? WHERE id=1", (xp, xp))
    conn.commit()
    stats = c.execute("SELECT total_xp FROM user_stats WHERE id=1").fetchone()
    conn.close()
    return jsonify({"total_xp": stats["total_xp"]})

@app.route("/get-user-stats")
def get_user_stats():
    conn = get_db()
    stats = conn.execute("SELECT * FROM user_stats WHERE id=1").fetchone()
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


# =========================================================
# RUN
# =========================================================
if __name__ == "__main__":
    init_db()
    app.run(debug=True)