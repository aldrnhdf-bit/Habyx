from flask import Blueprint, request, jsonify
from auth_utils import login_required, current_user_id
from database import get_db
from nutrition_api import search_usda_foods

nutrition = Blueprint('nutrition', __name__)

@nutrition.route("/save-meal", methods=["POST"])
@login_required
def save_meal():
    data = request.get_json()
    conn = get_db()
    conn.execute("INSERT INTO meals (user_id, name, meal_type, calories, protein, carbs, fat) VALUES (?,?,?,?,?,?,?)",
                 (current_user_id(), data["name"], data["meal_type"], data["calories"],
                  data.get("protein", 0), data.get("carbs", 0), data.get("fat", 0)))
    conn.commit(); conn.close()
    return jsonify({"status": "saved"})

@nutrition.route("/get-meals/<meal_type>")
@login_required
def get_meals(meal_type):
    conn = get_db()
    rows = conn.execute("SELECT * FROM meals WHERE user_id=? AND meal_type=?", (current_user_id(), meal_type)).fetchall()
    conn.close()
    return jsonify([{"id": r["id"], "name": r["name"], "calories": r["calories"],
                     "protein": r["protein"], "carbs": r["carbs"], "fat": r["fat"]} for r in rows])

@nutrition.route("/search-food", methods=["POST"])
def search_food():
    data = request.get_json()
    query = data.get("food", "")
    return jsonify({"foods": search_usda_foods(query)})
