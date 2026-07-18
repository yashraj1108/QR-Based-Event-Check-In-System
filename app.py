import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, jsonify, flash

from config import Config
from models import db, Attendee
from qr_utils import generate_ticket_code, generate_qr_code


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)
    os.makedirs(app.config["QR_CODE_DIR"], exist_ok=True)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    register_routes(app)
    return app


def register_routes(app):

    # ---------- Pages ----------

    @app.route("/")
    def index():
        return render_template("index.html", event_name=app.config["EVENT_NAME"])

    @app.route("/register", methods=["POST"])
    def register():
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        ticket_type = request.form.get("ticket_type", "General")

        if not name or not email:
            flash("Name and email are required.", "error")
            return redirect(url_for("index"))

        if Attendee.query.filter_by(email=email).first():
            flash("That email is already registered for this event.", "error")
            return redirect(url_for("index"))

        ticket_code = generate_ticket_code()
        attendee = Attendee(name=name, email=email, ticket_type=ticket_type, ticket_code=ticket_code)
        db.session.add(attendee)
        db.session.commit()

        generate_qr_code(ticket_code, f"{ticket_code}.png", app.config["QR_CODE_DIR"])

        return redirect(url_for("ticket", ticket_code=ticket_code))

    @app.route("/ticket/<ticket_code>")
    def ticket(ticket_code):
        attendee = Attendee.query.filter_by(ticket_code=ticket_code).first_or_404()
        return render_template("ticket.html", attendee=attendee, event_name=app.config["EVENT_NAME"])

    @app.route("/scan")
    def scan():
        return render_template("scan.html", event_name=app.config["EVENT_NAME"])

    @app.route("/dashboard")
    def dashboard():
        return render_template("dashboard.html", event_name=app.config["EVENT_NAME"])

    @app.route("/attendees")
    def attendees():
        all_attendees = Attendee.query.order_by(Attendee.created_at.desc()).all()
        return render_template("attendees.html", attendees=all_attendees, event_name=app.config["EVENT_NAME"])

    # ---------- JSON API (used by the scanner + dashboard) ----------

    @app.route("/api/checkin", methods=["POST"])
    def api_checkin():
        data = request.get_json(silent=True) or {}
        code = (data.get("code") or "").strip()

        if not code:
            return jsonify({"status": "error", "message": "No code provided."}), 400

        attendee = Attendee.query.filter_by(ticket_code=code).first()

        if not attendee:
            return jsonify({"status": "invalid", "message": "Ticket not recognized."}), 404

        if attendee.is_checked_in:
            return jsonify({
                "status": "duplicate",
                "message": f"{attendee.name} already checked in at "
                           f"{attendee.checkin_time.strftime('%H:%M:%S')}.",
                "attendee": attendee.to_dict(),
            }), 409

        attendee.is_checked_in = True
        attendee.checkin_time = datetime.utcnow()
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": f"Welcome, {attendee.name}!",
            "attendee": attendee.to_dict(),
        })

    @app.route("/api/stats")
    def api_stats():
        total = Attendee.query.count()
        checked_in = Attendee.query.filter_by(is_checked_in=True).count()
        percent = round((checked_in / total) * 100, 1) if total else 0.0
        return jsonify({
            "total": total,
            "checked_in": checked_in,
            "remaining": total - checked_in,
            "percent": percent,
        })

    @app.route("/api/feed")
    def api_feed():
        recent = (
            Attendee.query.filter_by(is_checked_in=True)
            .order_by(Attendee.checkin_time.desc())
            .limit(10)
            .all()
        )
        return jsonify([a.to_dict() for a in recent])


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
