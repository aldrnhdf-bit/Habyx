from flask import Flask
from database import init_db

# Import blueprints
from routes.auth import auth
from routes.pages import pages
from routes.feed import feed
from routes.activities import activities
from routes.workouts import workouts
from routes.cardio import cardio
from routes.hydration import hydration
from routes.hygiene import hygiene
from routes.nutrition import nutrition
from routes.xp import xp

app = Flask(__name__)
app.secret_key = "habyx_secret_key_2026"

# Register blueprints
app.register_blueprint(auth)
app.register_blueprint(pages)
app.register_blueprint(feed)
app.register_blueprint(activities)
app.register_blueprint(workouts)
app.register_blueprint(cardio)
app.register_blueprint(hydration)
app.register_blueprint(hygiene)
app.register_blueprint(nutrition)
app.register_blueprint(xp)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
