from flask import Blueprint, jsonify
from auth_utils import login_required, current_user_id
from database import get_db

feed = Blueprint('feed', __name__)

@feed.route("/get-dashboard")
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

@feed.route("/delete-workout/<int:id>", methods=["DELETE"])
@login_required
def delete_workout(id):
    conn = get_db()
    conn.execute("DELETE FROM workouts WHERE id=? AND user_id=?", (id, current_user_id()))
    conn.commit(); conn.close()
    return jsonify({"status": "deleted"})

@feed.route("/delete-cardio/<int:id>", methods=["DELETE"])
@login_required
def delete_cardio(id):
    conn = get_db()
    conn.execute("DELETE FROM cardio WHERE id=? AND user_id=?", (id, current_user_id()))
    conn.commit(); conn.close()
    return jsonify({"status": "deleted"})

@feed.route("/delete-meal/<int:id>", methods=["DELETE"])
@login_required
def delete_meal(id):
    conn = get_db()
    conn.execute("DELETE FROM meals WHERE id=? AND user_id=?", (id, current_user_id()))
    conn.commit(); conn.close()
    return jsonify({"status": "deleted"})

@feed.route("/delete-water/<int:id>", methods=["DELETE"])
@login_required
def delete_water(id):
    conn = get_db()
    conn.execute("DELETE FROM hydration WHERE id=? AND user_id=?", (id, current_user_id()))
    conn.commit(); conn.close()
    return jsonify({"status": "deleted"})

@feed.route("/delete-hygiene/<int:id>", methods=["DELETE"])
@login_required
def delete_hygiene(id):
    conn = get_db()
    conn.execute("DELETE FROM hygiene WHERE id=? AND user_id=?", (id, current_user_id()))
    conn.commit(); conn.close()
    return jsonify({"status": "deleted"})
