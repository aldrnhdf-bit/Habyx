from flask import Blueprint, request, jsonify
from auth_utils import login_required, current_user_id
from database import get_db

activities = Blueprint('activities', __name__)

@activities.route("/save-planned-task", methods=["POST"])
@login_required
def save_planned_task():
    data = request.get_json()
    uid = current_user_id()
    conn = get_db()
    conn.execute("INSERT INTO planned_tasks (user_id, task_name, task_type, day_of_week, time, completed) VALUES (?,?,?,?,?,0)",
                 (uid, data["task_name"], data["task_type"], data["day"], data["time"]))
    conn.commit(); conn.close()
    return jsonify({"status": "saved"})

@activities.route("/get-planned-tasks")
@login_required
def get_planned_tasks():
    uid = current_user_id()
    conn = get_db()
    rows = conn.execute("SELECT * FROM planned_tasks WHERE user_id=? ORDER BY day_of_week, time", (uid,)).fetchall()
    conn.close()
    return jsonify([{"id": r["id"], "task_name": r["task_name"], "task_type": r["task_type"],
                     "day": r["day_of_week"], "time": r["time"], "completed": r["completed"]} for r in rows])

@activities.route("/toggle-planned-task/<int:id>", methods=["POST"])
@login_required
def toggle_planned_task(id):
    data = request.get_json()
    conn = get_db()
    conn.execute("UPDATE planned_tasks SET completed=?, date_completed=? WHERE id=? AND user_id=?",
                 (data["completed"], data.get("date_completed"), id, current_user_id()))
    conn.commit(); conn.close()
    return jsonify({"status": "updated"})

@activities.route("/delete-planned-task/<int:id>", methods=["DELETE"])
@login_required
def delete_planned_task(id):
    conn = get_db()
    conn.execute("DELETE FROM planned_tasks WHERE id=? AND user_id=?", (id, current_user_id()))
    conn.commit(); conn.close()
    return jsonify({"status": "deleted"})

@activities.route("/reset-week", methods=["POST"])
@login_required
def reset_week():
    try:
        conn = get_db()
        conn.execute("UPDATE planned_tasks SET completed=0, date_completed=NULL WHERE user_id=?", (current_user_id(),))
        conn.commit(); conn.close()
        return jsonify({"status": "reset"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
