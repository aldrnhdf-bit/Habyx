import json
from pathlib import Path

from flask import Flask, abort, render_template

app = Flask(__name__)

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


@app.route("/")
def dashboard():
    try:
        dashboard_data = load_dashboard_data()
    except ValueError as exc:
        abort(500, description=str(exc))

    return render_template(
        "dashboard.html",
        **dashboard_data,
    )


if __name__ == "__main__":
    app.run(debug=True)
