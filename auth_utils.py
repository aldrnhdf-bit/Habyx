import hashlib
from functools import wraps

from flask import redirect, session, url_for


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated


def current_user_id():
    return session.get("user_id", 1)
