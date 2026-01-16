from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import date
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Backend is alive"

if __name__ == "__main__":
    app.run()


app = Flask(__name__)
CORS(app)

START_DATE = date(2026, 1, 1)


# -------------------- DB --------------------
def get_db():
    return sqlite3.connect("database.db")


# -------------------- HELPERS --------------------
def is_periodic_day():
    return (date.today() - START_DATE).days % 4 == 0


def todays_workout():
    plan = {
        0: {
            "name": "Chest + Triceps",
            "exercises": [
                "Push-ups",
                "Dumbbell Floor Press",
                "Dumbbell Fly",
                "Overhead Triceps Extension",
                "Close-grip Push-ups",
                "20 Sprints"
            ]
        },
        1: {
            "name": "Back + Biceps",
            "exercises": [
                "One-arm Dumbbell Row",
                "Dumbbell Deadlift",
                "Reverse Fly",
                "Standing Dumbbell Curl",
                "Hammer Curl",
                "20 Sprints"
            ]
        },
        2: {
            "name": "Shoulders + Core",
            "exercises": [
                "Overhead Dumbbell Press",
                "Lateral Raises",
                "Front Raises",
                "Plank",
                "Leg Raises (ankle weights)",
                "20 Sprints"
            ]
        },
        3: {
            "name": "Legs",
            "exercises": [
                "Squats (rod)",
                "Lunges (ankle weights)",
                "Romanian Deadlift",
                "Calf Raises",
                "20 Sprints"
            ]
        },
        4: {
            "name": "Arms (Biceps + Triceps)",
            "exercises": [
                "Concentration Curls",
                "Wide-grip Curls",
                "Skull Crushers",
                "Triceps Kickbacks",
                "20 Sprints"
            ]
        },
        5: {
            "name": "Full Body",
            "exercises": [
                "Push-ups",
                "Dumbbell Rows",
                "Shoulder Press",
                "Squats",
                "Core of choice",
                "20 Sprints"
            ]
        },
        6: {
            "name": "Recovery + Light Cardio",
            "exercises": [
                "Brisk Walk / Jog",
                "Mobility Stretching",
                "Light Core",
                "20 Light Sprints"
            ]
        }
    }
    return plan[date.today().weekday()]


# -------------------- WATER --------------------
@app.route("/water", methods=["GET", "POST"])
def water():
    today = str(date.today())
    db = get_db()
    cur = db.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS water (
            day TEXT PRIMARY KEY,
            amount INTEGER
        )
    """)

    if request.method == "POST":
        amount = request.json.get("amount", 0)
        cur.execute(
            "INSERT OR REPLACE INTO water VALUES (?, ?)",
            (today, amount)
        )
        db.commit()
        db.close()
        return jsonify({"status": "saved"})

    cur.execute("SELECT amount FROM water WHERE day = ?", (today,))
    row = cur.fetchone()
    db.close()
    return jsonify({"amount": row[0] if row else 0})


@app.route("/water/history")
def water_history():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT day, amount FROM water ORDER BY day DESC")
    rows = cur.fetchall()
    db.close()
    return jsonify([{"day": d, "amount": a} for d, a in rows])


# -------------------- SKINCARE --------------------
@app.route("/skincare/daily", methods=["GET", "POST"])
def skincare_daily():
    today = str(date.today())
    db = get_db()
    cur = db.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS skincare_daily (
            day TEXT PRIMARY KEY,
            m_facewash INTEGER,
            m_moisturizer INTEGER,
            m_sunscreen INTEGER,
            a_facewash INTEGER,
            a_moisturizer INTEGER,
            a_sunscreen INTEGER,
            limcee INTEGER,
            n_facewash INTEGER,
            n_treatment INTEGER,
            n_niacinamide INTEGER
        )
    """)

    if request.method == "POST":
        data = request.json
        cur.execute("""
            INSERT OR REPLACE INTO skincare_daily
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            today,
            data.get("m_facewash", 0),
            data.get("m_moisturizer", 0),
            data.get("m_sunscreen", 0),
            data.get("a_facewash", 0),
            data.get("a_moisturizer", 0),
            data.get("a_sunscreen", 0),
            data.get("limcee", 0),
            data.get("n_facewash", 0),
            data.get("n_treatment", 0),
            data.get("n_niacinamide", 0)
        ))
        db.commit()
        db.close()
        return jsonify({"status": "saved"})

    cur.execute("SELECT * FROM skincare_daily WHERE day = ?", (today,))
    row = cur.fetchone()
    db.close()

    if not row:
        return jsonify({})

    keys = [
        "day","m_facewash","m_moisturizer","m_sunscreen",
        "a_facewash","a_moisturizer","a_sunscreen",
        "limcee","n_facewash","n_treatment","n_niacinamide"
    ]
    return jsonify(dict(zip(keys, row)))


@app.route("/skincare/periodic/reminder")
def skincare_periodic_reminder():
    return jsonify({"due": is_periodic_day()})


# -------------------- EXERCISE --------------------
@app.route("/exercise/today", methods=["GET", "POST"])
def exercise_today():
    today = str(date.today())
    workout = todays_workout()

    db = get_db()
    cur = db.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS exercise_daily (
            day TEXT PRIMARY KEY,
            workout TEXT,
            done INTEGER,
            minutes INTEGER
        )
    """)

    if request.method == "POST":
        data = request.json
        cur.execute("""
            INSERT OR REPLACE INTO exercise_daily
            VALUES (?, ?, ?, ?)
        """, (
            today,
            workout["name"],
            data.get("done", 0),
            data.get("minutes", 0)
        ))
        db.commit()
        db.close()
        return jsonify({"status": "saved"})

    cur.execute("SELECT done, minutes FROM exercise_daily WHERE day = ?", (today,))
    row = cur.fetchone()
    db.close()

    return jsonify({
        "workout": workout["name"],
        "exercises": workout["exercises"],
        "done": row[0] if row else 0,
        "minutes": row[1] if row else 0
    })


@app.route("/communication/daily", methods=["GET", "POST"])
def communication_daily():
    today = str(date.today())
    db = get_db()
    cur = db.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS communication_daily (
            day TEXT PRIMARY KEY,
            spoke_confidently INTEGER,
            avoided_fillers INTEGER,
            eye_contact INTEGER,
            reflection TEXT
        )
    """)

    if request.method == "POST":
        data = request.json
        cur.execute("""
            INSERT OR REPLACE INTO communication_daily
            VALUES (?, ?, ?, ?, ?)
        """, (
            today,
            data.get("spoke_confidently", 0),
            data.get("avoided_fillers", 0),
            data.get("eye_contact", 0),
            data.get("reflection", "")
        ))
        db.commit()
        db.close()
        return jsonify({"status": "saved"})

    cur.execute("SELECT * FROM communication_daily WHERE day = ?", (today,))
    row = cur.fetchone()
    db.close()

    if not row:
        return jsonify({})

    keys = ["day", "spoke_confidently", "avoided_fillers", "eye_contact", "reflection"]
    return jsonify(dict(zip(keys, row)))



@app.route("/reading/daily", methods=["GET", "POST"])
def reading_daily():
    today = str(date.today())
    db = get_db()
    cur = db.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS reading_daily (
            day TEXT PRIMARY KEY,
            reading_minutes INTEGER,
            japanese_minutes INTEGER,
            notes TEXT
        )
    """)

    if request.method == "POST":
        data = request.json
        cur.execute("""
            INSERT OR REPLACE INTO reading_daily
            VALUES (?, ?, ?, ?)
        """, (
            today,
            data.get("reading_minutes", 0),
            data.get("japanese_minutes", 0),
            data.get("notes", "")
        ))
        db.commit()
        db.close()
        return jsonify({"status": "saved"})

    cur.execute("SELECT * FROM reading_daily WHERE day = ?", (today,))
    row = cur.fetchone()
    db.close()

    if not row:
        return jsonify({})

    keys = ["day", "reading_minutes", "japanese_minutes", "notes"]
    return jsonify(dict(zip(keys, row)))


@app.route("/skill/diary", methods=["GET", "POST"])
def skill_diary():
    today = str(date.today())
    db = get_db()
    cur = db.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS skill_diary (
            day TEXT PRIMARY KEY,
            entry TEXT
        )
    """)

    if request.method == "POST":
        data = request.json
        cur.execute("""
            INSERT OR REPLACE INTO skill_diary
            VALUES (?, ?)
        """, (today, data.get("entry", "")))
        db.commit()
        db.close()
        return jsonify({"status": "saved"})

    cur.execute("SELECT entry FROM skill_diary WHERE day = ?", (today,))
    row = cur.fetchone()
    db.close()

    return jsonify({"entry": row[0] if row else ""})



@app.route("/communication/weekly", methods=["GET"])
def communication_weekly():
    db = get_db()
    cur = db.cursor()

    cur.execute("""
        SELECT
            COUNT(*) as total_days,
            SUM(spoke_confidently),
            SUM(avoided_fillers),
            SUM(eye_contact)
        FROM communication_daily
        WHERE day >= date('now','-6 days')
    """)
    row = cur.fetchone()
    db.close()

    return jsonify({
        "days_logged": row[0] or 0,
        "confident_days": row[1] or 0,
        "filler_free_days": row[2] or 0,
        "eye_contact_days": row[3] or 0
    })


@app.route("/skill/weekly", methods=["GET"])
def skill_weekly():
    db = get_db()
    cur = db.cursor()

    cur.execute("""
        SELECT day, entry
        FROM skill_diary
        WHERE day >= date('now','-6 days')
        ORDER BY day DESC
    """)
    rows = cur.fetchall()
    db.close()

    return jsonify([
        {"day": d, "entry": e}
        for d, e in rows
    ])


# -------------------- RUN (LAST LINE ONLY) --------------------
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)



