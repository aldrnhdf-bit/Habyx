from flask import Blueprint, request, jsonify
from auth_utils import login_required, current_user_id
from database import get_db
from datetime import datetime, timedelta

xp = Blueprint('xp', __name__)

@xp.route("/add-xp", methods=["POST"])
@login_required
def add_xp():
    data = request.get_json()
    xp_amount = data.get("xp", 5)
    uid = current_user_id()
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO user_stats (id, user_id) VALUES (?,?)", (uid, uid))
    
    # Get current stats
    stats = c.execute("SELECT total_xp, current_xp FROM user_stats WHERE user_id=?", (uid,)).fetchone()
    current_total = stats["total_xp"]
    current_level_xp = stats["current_xp"]
    
    # Calculate new values
    new_total = max(0, current_total + xp_amount)  # Total XP can't go below 0
    new_level_xp = (new_total % 50)  # Current level XP (0-49)
    
    c.execute("UPDATE user_stats SET total_xp=?, current_xp=? WHERE user_id=?", (new_total, new_level_xp, uid))
    conn.commit()
    final_stats = c.execute("SELECT total_xp FROM user_stats WHERE user_id=?", (uid,)).fetchone()
    conn.close()
    return jsonify({"total_xp": final_stats["total_xp"]})

@xp.route("/get-user-stats")
@login_required
def get_user_stats():
    uid = current_user_id()
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO user_stats (id, user_id) VALUES (?,?)", (uid, uid))
    conn.commit()
    stats = c.execute("SELECT * FROM user_stats WHERE user_id=?", (uid,)).fetchone()
    
    # Get tasks_completed count
    tasks_completed = c.execute("SELECT COUNT(*) as count FROM planned_tasks WHERE user_id=? AND completed=1", (uid,)).fetchone()["count"]
    
    # Get today's hydration
    today = datetime.now().strftime("%Y-%m-%d")
    today_hydration = c.execute("SELECT COALESCE(SUM(amount_ml), 0) as total FROM hydration WHERE user_id=? AND DATE(time) = ?", (uid, today)).fetchone()["total"]
    
    # Get week_completed (days this week with at least one completed task)
    today = datetime.now()
    # Calculate the start of this week (Monday)
    days_since_monday = today.weekday()
    week_start = today - timedelta(days=days_since_monday)
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    week_completed_data = c.execute("""
        SELECT COUNT(DISTINCT DATE(date_completed)) as count 
        FROM planned_tasks 
        WHERE user_id=? AND completed=1 AND DATE(date_completed) >= ?
    """, (uid, week_start.strftime("%Y-%m-%d"))).fetchone()
    week_completed = week_completed_data["count"] if week_completed_data else 0
    
    conn.close()
    
    if stats:
        return jsonify({
            "level": stats["level"],
            "current_xp": stats["current_xp"],
            "total_xp": stats["total_xp"],
            "current_streak": stats["current_streak"],
            "longest_streak": stats["longest_streak"],
            "tasks_completed": tasks_completed,
            "today_hydration": today_hydration,
            "week_completed": week_completed
        })
    return jsonify({"error": "No stats found"})

@xp.route("/get-username")
@login_required
def get_username():
    return jsonify({"username": __import__('flask').session.get("username", "User")})
