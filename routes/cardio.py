from flask import Blueprint, request, jsonify
from auth_utils import login_required, current_user_id
from database import get_db

cardio = Blueprint('cardio', __name__)

@cardio.route("/save-cardio", methods=["POST"])
@login_required
def save_cardio():
    data = request.get_json()
    conn = get_db()
    conn.execute("INSERT INTO cardio (user_id, activity, duration, intensity) VALUES (?,?,?,?)",
                 (current_user_id(), data["activity"], data["duration"], data["intensity"]))
    conn.commit(); conn.close()
    return jsonify({"status": "saved"})
