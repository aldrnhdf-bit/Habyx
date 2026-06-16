from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def dashboard():
    user = {
        "name": "Qhezrul Zinedine",
        "title": "Habyx",
        "avatar_initials": "QZ",
    }

    stats = [
        {"label": "Current Streak", "value": "18", "unit": "days", "accent": "violet"},
        {"label": "Current Level", "value": "7", "unit": "level", "accent": "blue"},
        {"label": "Current XP", "value": "2,430", "unit": "xp", "accent": "orange"},
        {"label": "Achievements", "value": "12", "unit": "badges", "accent": "green"},
    ]

    xp = {
        "level": 7,
        "current": 2430,
        "next_level": 3000,
        "percent": 81,
        "remaining": 570,
    }

    habits = [
        {
            "name": "Morning stretch",
            "time": "7:15 AM",
            "category": "Energy",
            "completed": True,
            "xp": 45,
        },
        {
            "name": "Drink 2L water",
            "time": "All day",
            "category": "Health",
            "completed": True,
            "xp": 35,
        },
        {
            "name": "Read 10 pages",
            "time": "8:30 PM",
            "category": "Mind",
            "completed": False,
            "xp": 50,
        },
        {
            "name": "No phone wind-down",
            "time": "10:00 PM",
            "category": "Sleep",
            "completed": False,
            "xp": 60,
        },
    ]

    ai_coach = {
        "message": "You finish health habits most consistently before noon. Try moving reading to lunch today for an easy XP win.",
        "focus": "Best next habit: Read 10 pages",
    }

    achievements = [
        {
            "name": "18-Day Flame",
            "description": "Kept your streak alive for 18 days.",
            "unlocked": True,
        },
        {
            "name": "Hydration Hero",
            "description": "Completed water goals five times this week.",
            "unlocked": True,
        },
        {
            "name": "Night Owl Reset",
            "description": "Complete wind-down three nights in a row.",
            "unlocked": False,
        },
        {
            "name": "Level 8 Spark",
            "description": "Reach Level 8 with 3,000 total XP.",
            "unlocked": False,
        },
    ]

    weekly_completion = {
        "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "values": [72, 86, 64, 92, 78, 88, 95],
    }

    return render_template(
        "dashboard.html",
        user=user,
        stats=stats,
        xp=xp,
        habits=habits,
        ai_coach=ai_coach,
        achievements=achievements,
        weekly_completion=weekly_completion,
    )


if __name__ == "__main__":
    app.run(debug=True)
