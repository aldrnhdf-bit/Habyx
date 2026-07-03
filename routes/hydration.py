from flask import Blueprint, request, jsonify
from auth_utils import login_required, current_user_id
from database import get_db
from datetime import datetime

hydration = Blueprint('hydration', __name__)

@hydration.route("/save-water", methods=["POST"])
@login_required
def save_water():
    data = request.get_json()
    conn = get_db()
    conn.execute("INSERT INTO hydration (user_id, amount_ml) VALUES (?,?)",
                 (current_user_id(), data["amount_ml"]))
    conn.commit(); conn.close()
    return jsonify({"status": "saved"})

@hydration.route("/get-today-hydration")
@login_required
def get_today_hydration():
    uid = current_user_id()
    today = datetime.now().strftime("%Y-%m-%d")
    
    conn = get_db()
    c = conn.cursor()
    
    # Sum all water logged today
    result = c.execute(
        "SELECT COALESCE(SUM(amount_ml), 0) as total_ml FROM hydration WHERE user_id=? AND DATE(time) = ?",
        (uid, today)
    ).fetchone()
    
    conn.close()
    
    total_ml = result["total_ml"] if result else 0
    daily_goal = 2000  # 2L daily goal
    
    # Allow percentage to exceed 100% for overflow visualization
    percentage = round((total_ml / daily_goal) * 100)
    
    return jsonify({
        "total_ml": total_ml,
        "daily_goal": daily_goal,
        "percentage": percentage
    })
