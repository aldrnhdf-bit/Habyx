from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'habyx-secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///habyx.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from .habits import habits
    app.register_blueprint(habits)

    return app

from datetime import date
from . import db

class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), default="General")

    streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)

    last_completed = db.Column(db.Date, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    @habits.route('/add-habit', methods=['POST'])
@login_required
def add_habit():

    name = request.form.get("name")
    category = request.form.get("category")

    if not name:
        return redirect('/habits')

    habit = Habit(
        name=name,
        category=category,
        user_id=current_user.id
    )

    db.session.add(habit)
    db.session.commit()

    return redirect('/habits')

@habits.route('/delete/<int:habit_id>')
@login_required
def delete_habit(habit_id):

    habit = Habit.query.get(habit_id)

    if habit and habit.user_id == current_user.id:
        db.session.delete(habit)
        db.session.commit()

    return redirect('/habits')