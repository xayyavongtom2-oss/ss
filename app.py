import os, time, secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
# Render terminates HTTPS at its proxy; trust forwarded scheme/host so generated
# pairing links use the public HTTPS URL required by mobile camera permissions.
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret-before-deploying")
db_url = os.environ.get("DATABASE_URL", "sqlite:///rope_counter.db")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
elif db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    jumps = db.Column(db.Integer, nullable=False, default=0)
    duration = db.Column(db.Integer, nullable=False, default=0)
    calories = db.Column(db.Float, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", backref=db.backref("workouts", lazy=True))

with app.app_context():
    db.create_all()

def login_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapped

def current_user():
    return db.session.get(User, session.get("user_id"))

@app.route("/")
def index():
    return redirect(url_for("dashboard") if session.get("user_id") else url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if len(username) < 3 or len(password) < 6 or "@" not in email:
            flash("ກະລຸນາກວດຊື່, ອີເມວ ແລະລະຫັດຜ່ານ (ຢ່າງໜ້ອຍ 6 ຕົວ).", "error")
        elif User.query.filter((User.username == username) | (User.email == email)).first():
            flash("ຊື່ຜູ້ໃຊ້ ຫຼື ອີເມວນີ້ຖືກໃຊ້ແລ້ວ.", "error")
        else:
            user = User(username=username, email=email, password_hash=generate_password_hash(password))
            db.session.add(user); db.session.commit()
            session["user_id"] = user.id
            flash("ສ້າງບັນຊີສຳເລັດ!", "success")
            return redirect(url_for("dashboard"))
    return render_template("auth.html", mode="register")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identity = request.form.get("identity", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter((User.username == identity) | (User.email == identity.lower())).first()
        if user and check_password_hash(user.password_hash, password):
            session.clear(); session["user_id"] = user.id
            return redirect(url_for("dashboard"))
        flash("ຊື່ບັນຊີ ຫຼື ລະຫັດຜ່ານບໍ່ຖືກຕ້ອງ.", "error")
    return render_template("auth.html", mode="login")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    workouts = Workout.query.filter_by(user_id=user.id).order_by(Workout.created_at.desc()).limit(7).all()
    total_jumps = db.session.query(db.func.coalesce(db.func.sum(Workout.jumps), 0)).filter_by(user_id=user.id).scalar()
    total_seconds = db.session.query(db.func.coalesce(db.func.sum(Workout.duration), 0)).filter_by(user_id=user.id).scalar()
    total_calories = db.session.query(db.func.coalesce(db.func.sum(Workout.calories), 0)).filter_by(user_id=user.id).scalar()
    return render_template("dashboard.html", user=user, workouts=workouts, total_jumps=total_jumps,
                           total_seconds=total_seconds, total_calories=round(total_calories))

def get_ice_servers():
    """Return public STUN plus optional TURN credentials configured in Render."""
    servers = [{"urls": "stun:stun.l.google.com:19302"}]
    turn_urls = [u.strip() for u in os.environ.get("TURN_URLS", "").split(",") if u.strip()]
    turn_username = os.environ.get("TURN_USERNAME", "").strip()
    turn_credential = os.environ.get("TURN_CREDENTIAL", "").strip()
    if turn_urls and turn_username and turn_credential:
        servers.append({"urls": turn_urls, "username": turn_username, "credential": turn_credential})
    return servers

@app.route("/camera")
@login_required
def camera():
    return render_template("camera.html", user=current_user(), ice_servers=get_ice_servers())

@app.route("/leaderboard")
@login_required
def leaderboard():
    rows = db.session.query(User.username, db.func.sum(Workout.jumps).label("score")).join(Workout).group_by(User.id).order_by(db.desc("score")).limit(50).all()
    my_rank = next((i for i, row in enumerate(rows, 1) if row.username == current_user().username), None)
    return render_template("leaderboard.html", rows=rows, my_rank=my_rank, user=current_user())

@app.route("/history")
@login_required
def history():
    workouts = Workout.query.filter_by(user_id=session["user_id"]).order_by(Workout.created_at.desc()).all()
    return render_template("history.html", workouts=workouts, user=current_user())

@app.route("/achievements")
@login_required
def achievements():
    total = db.session.query(db.func.coalesce(db.func.sum(Workout.jumps), 0)).filter_by(user_id=session["user_id"]).scalar()
    return render_template("achievements.html", total=total, user=current_user())

@app.post("/api/workout")
@login_required
def save_workout():
    data = request.get_json(silent=True) or {}
    try:
        jumps = max(0, min(int(data.get("jumps", 0)), 100000))
        duration = max(0, min(int(data.get("duration", 0)), 86400))
    except (TypeError, ValueError):
        return jsonify(ok=False, error="Invalid workout data"), 400
    if jumps == 0 and duration == 0:
        return jsonify(ok=False, error="No workout data"), 400
    calories = round(jumps * 0.08, 1)
    workout = Workout(user_id=session["user_id"], jumps=jumps, duration=duration, calories=calories)
    db.session.add(workout); db.session.commit()
    return jsonify(ok=True, id=workout.id)


# Lightweight WebRTC signaling. Use a single web-service instance or replace
# this in-memory store with Redis for multi-instance production deployments.
SIGNAL_ROOMS = {}

@app.post("/api/pair")
@login_required
def create_pair():
    code = secrets.token_urlsafe(6).replace("-", "").replace("_", "")[:8].upper()
    SIGNAL_ROOMS[code] = {"messages": [], "created": time.time()}
    return jsonify(ok=True, code=code, phone_url=url_for("phone_camera", code=code, _external=True))

@app.route("/phone/<code>")
def phone_camera(code):
    if code not in SIGNAL_ROOMS:
        return render_template("phone.html", code=code, invalid=True, ice_servers=get_ice_servers())
    return render_template("phone.html", code=code, invalid=False, ice_servers=get_ice_servers())

@app.route("/api/signal/<code>", methods=["GET", "POST"])
def signaling(code):
    room = SIGNAL_ROOMS.get(code)
    if not room or time.time() - room["created"] > 3600:
        SIGNAL_ROOMS.pop(code, None)
        return jsonify(ok=False, error="Pairing code expired"), 404
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        sender = data.get("sender")
        kind = data.get("kind")
        if sender not in ("pc", "phone") or kind not in ("offer", "answer", "candidate", "bye"):
            return jsonify(ok=False), 400
        room["messages"].append({"id": len(room["messages"]), "sender": sender,
                                 "kind": kind, "payload": data.get("payload")})
        return jsonify(ok=True)
    sender = request.args.get("sender")
    try:
        after = max(-1, int(request.args.get("after", -1)))
    except ValueError:
        after = -1
    if sender not in ("pc", "phone"):
        return jsonify(ok=False), 400
    messages = [m for m in room["messages"] if m["sender"] != sender and m["id"] > after]
    return jsonify(ok=True, messages=messages)


@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
