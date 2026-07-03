from flask import Blueprint, request, jsonify
from auth_utils import login_required, current_user_id
from database import get_db

workouts = Blueprint('workouts', __name__)

@workouts.route("/save-workout", methods=["POST"])
@login_required
def save_workout():
    data = request.get_json()
    conn = get_db()
    conn.execute("INSERT INTO workouts (user_id, name, body_part) VALUES (?,?,?)",
                 (current_user_id(), data["name"], data["body_part"]))
    conn.commit(); conn.close()
    return jsonify({"status": "saved"})

@workouts.route("/get-workouts")
@login_required
def get_workouts():
    conn = get_db()
    rows = conn.execute("SELECT * FROM workouts WHERE user_id=? ORDER BY id DESC", (current_user_id(),)).fetchall()
    conn.close()
    return jsonify([{"id": r["id"], "name": r["name"], "body_part": r["body_part"]} for r in rows])
