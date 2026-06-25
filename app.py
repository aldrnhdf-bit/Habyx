import json
from pathlib import Path

from flask import Flask, abort, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = "habyx-dashboard-dev-key"

BASE_DIR = Path(__file__).resolve().parent
USER_DATA_FILE = BASE_DIR / "user.txt"
REQUIRED_DATA_SECTIONS = (
    "user",
    "stats",
    "xp",
    "habits",
    "ai_coach",
    "achievements",
    "weekly_completion",
)


def get_initials(name):
    words = [word for word in name.strip().split() if word]
    if not words:
        return "HX"

    return "".join(word[0].upper() for word in words[:2])


def get_int(value, fallback=0):
    try:
        return max(int(str(value).replace(",", "").strip()), 0)
    except (TypeError, ValueError):
        return fallback


def load_dashboard_data(data_file=USER_DATA_FILE):
    try:
        raw_data = data_file.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"Missing data file: {data_file.name}") from exc

    try:
        dashboard_data = json.loads(raw_data)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"{data_file.name} must contain valid JSON. Error on line {exc.lineno}."
        ) from exc

    missing_sections = [
        section for section in REQUIRED_DATA_SECTIONS if section not in dashboard_data
    ]
    if missing_sections:
        missing = ", ".join(missing_sections)
        raise ValueError(f"{data_file.name} is missing required section(s): {missing}.")

    return dashboard_data


def build_login_data(form, dashboard_data):
    user = dashboard_data["user"]
    xp = dashboard_data["xp"]
    stats = dashboard_data["stats"]

    name = form.get("name", "").strip() or user["name"]
    title = form.get("title", "").strip() or user["title"]
    username = form.get("username", "").strip()
    email = form.get("email", "").strip()
    focus = form.get("focus", "").strip()
    level = get_int(form.get("level"), xp["level"])
    current_xp = get_int(form.get("current_xp"), xp["current"])
    next_level = get_int(form.get("next_level"), xp["next_level"])
    streak = get_int(form.get("streak"), get_int(stats[0]["value"]))
    achievements = get_int(form.get("achievements"), get_int(stats[3]["value"]))

    return {
        "name": name,
        "title": title,
        "username": username,
        "email": email,
        "focus": focus,
        "avatar_initials": get_initials(name),
        "level": level,
        "current_xp": current_xp,
        "next_level": next_level,
        "streak": streak,
        "achievements": achievements,
    }


def apply_login_data(dashboard_data, login_data):
    dashboard_data["user"].update(
        {
            "name": login_data["name"],
            "title": login_data["title"],
            "avatar_initials": login_data["avatar_initials"],
            "username": login_data["username"],
            "email": login_data["email"],
            "focus": login_data["focus"],
        }
    )

    current_xp = login_data["current_xp"]
    next_level = max(login_data["next_level"], 1)
    remaining = max(next_level - current_xp, 0)
    percent = min(round((current_xp / next_level) * 100), 100)

    dashboard_data["stats"] = [
        {
            "label": "Current Streak",
            "value": str(login_data["streak"]),
            "unit": "days",
            "accent": "violet",
        },
        {
            "label": "Current Level",
            "value": str(login_data["level"]),
            "unit": "level",
            "accent": "blue",
        },
        {
            "label": "Current XP",
            "value": f"{current_xp:,}",
            "unit": "xp",
            "accent": "orange",
        },
        {
            "label": "Achievements",
            "value": str(login_data["achievements"]),
            "unit": "badges",
            "accent": "green",
        },
    ]
    dashboard_data["xp"].update(
        {
            "level": login_data["level"],
            "current": current_xp,
            "next_level": next_level,
            "percent": percent,
            "remaining": remaining,
        }
    )

    if login_data["focus"]:
        dashboard_data["ai_coach"] = {
            "focus": f"Today's focus: {login_data['focus']}",
            "message": (
                f"Welcome back, {login_data['name']}. Your dashboard is showing "
                "the data you entered during login."
            ),
        }

    return dashboard_data


def get_dashboard_context():
    try:
        dashboard_data = load_dashboard_data()
    except ValueError as exc:
        abort(500, description=str(exc))

    login_data = session.get("login_data")
    if login_data:
        dashboard_data = apply_login_data(dashboard_data, login_data)

    login_details = []
    if login_data:
        login_details = [
            ("Name", login_data["name"]),
            ("Username", login_data["username"] or "Not provided"),
            ("Email", login_data["email"] or "Not provided"),
            ("Dashboard title", login_data["title"]),
            ("Focus", login_data["focus"] or "Not provided"),
            ("Level", login_data["level"]),
            ("Current XP", f"{login_data['current_xp']:,}"),
            ("XP for next level", f"{login_data['next_level']:,}"),
            ("Streak", f"{login_data['streak']} days"),
            ("Achievements", f"{login_data['achievements']} badges"),
        ]

    dashboard_data["login_details"] = login_details
    dashboard_data["is_logged_in"] = bool(login_data)
    return dashboard_data


@app.route("/login", methods=["GET", "POST"])
def login():
    dashboard_data = get_dashboard_context()

    if request.method == "POST":
        session["login_data"] = build_login_data(request.form, dashboard_data)
        return redirect(url_for("dashboard"))

    return render_template(
        "login.html",
        user=dashboard_data["user"],
        xp=dashboard_data["xp"],
        stats=dashboard_data["stats"],
    )


@app.route("/logout")
def logout():
    session.pop("login_data", None)
    return redirect(url_for("login"))


@app.route("/")
def dashboard():
    dashboard_data = get_dashboard_context()

    return render_template(
        "dashboard.html",
        **dashboard_data,
    )


if __name__ == "__main__":
    app.run(debug=True)
