from flask import Blueprint, request, jsonify
from auth_utils import login_required, current_user_id
from database import get_db

hygiene = Blueprint('hygiene', __name__)

@hygiene.route("/save-hygiene", methods=["POST"])
@login_required
def save_hygiene():
    data = request.get_json()
    conn = get_db()
    conn.execute("INSERT INTO hygiene (user_id, task, time_of_day) VALUES (?,?,?)",
                 (current_user_id(), data["task"], data["time_of_day"]))
    conn.commit(); conn.close()
    return jsonify({"status": "saved"})
