from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


def get_conn():
    return sqlite3.connect("database.db")


def setup_database():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    with open("db/setup.sql", "r", encoding="utf-8") as f:
        cur.executescript(f.read())

    conn.commit()
    conn.close()


@app.route("/")
def intro():
    return render_template("intro.html")


@app.route("/defencepage/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Allowing anything as requested, and redirecting straight to dashboard
        return redirect("/defencepage")
    return render_template("login.html")


@app.route("/defencepage")
def index():
    conn = get_conn()
    cur = conn.cursor()

    search_query = request.args.get('search', '').strip()

    if search_query:
        search_term = f"%{search_query}%"
        alerts = cur.execute("SELECT * FROM Alerts WHERE message LIKE ? OR object_id LIKE ? ORDER BY created_at DESC", (search_term, search_term)).fetchall()
        threats = cur.execute("SELECT * FROM Threat_Assessment WHERE threat_level LIKE ? OR object_id LIKE ? ORDER BY assessed_at DESC", (search_term, search_term)).fetchall()
        audit_logs = cur.execute("SELECT * FROM Audit_Log WHERE action LIKE ? OR details LIKE ? OR object_id LIKE ? ORDER BY timestamp DESC LIMIT 50", (search_term, search_term, search_term)).fetchall()
    else:
        alerts = cur.execute("SELECT * FROM Alerts ORDER BY created_at DESC").fetchall()
        threats = cur.execute("SELECT * FROM Threat_Assessment ORDER BY assessed_at DESC").fetchall()
        audit_logs = cur.execute("SELECT * FROM Audit_Log ORDER BY timestamp DESC LIMIT 50").fetchall()

    conn.close()

    return render_template("index.html", alerts=alerts, threats=threats, audit_logs=audit_logs, search=search_query)


@app.route("/defencepage/add", methods=["POST"])
def add():
    obj_type = request.form["type"]
    speed = int(request.form["speed"])
    altitude = int(request.form["altitude"])

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO Aerial_Objects (type, speed, altitude)
    VALUES (?, ?, ?)
    """, (obj_type, speed, altitude))

    conn.commit()
    conn.close()

    return redirect("/defencepage")


@app.route("/defencepage/delete/<int:id>", methods=["POST"])
def delete_record(id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM Aerial_Objects WHERE object_id = ?", (id,))
    cur.execute("DELETE FROM Threat_Assessment WHERE object_id = ?", (id,))
    cur.execute("DELETE FROM Alerts WHERE object_id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/defencepage")


@app.route("/defencepage/edit/<int:id>")
def edit(id):
    conn = get_conn()
    cur = conn.cursor()
    obj = cur.execute("SELECT * FROM Aerial_Objects WHERE object_id = ?", (id,)).fetchone()
    conn.close()
    if not obj:
        return redirect("/defencepage")
    return render_template("edit.html", obj=obj)


@app.route("/defencepage/update/<int:id>", methods=["POST"])
def update(id):
    obj_type = request.form["type"]
    speed = int(request.form["speed"])
    altitude = int(request.form["altitude"])

    conn = get_conn()
    cur = conn.cursor()

    # Update Aerial Object
    cur.execute("""
        UPDATE Aerial_Objects
        SET type = ?, speed = ?, altitude = ?
        WHERE object_id = ?
    """, (obj_type, speed, altitude, id))

    # Calculate new Threat Assessment
    threat_level = 'LOW'
    if obj_type == 'Missile' and speed > 900:
        threat_level = 'CRITICAL'
    elif speed > 800 and altitude < 2000:
        threat_level = 'HIGH'
    elif speed > 400:
        threat_level = 'MEDIUM'
        
    priority_score = 20
    if obj_type == 'Missile':
        priority_score = 100
    elif speed > 800:
        priority_score = 80
    elif speed > 400:
        priority_score = 50

    cur.execute("""
        UPDATE Threat_Assessment
        SET threat_level = ?, priority_score = ?, assessed_at = CURRENT_TIMESTAMP
        WHERE object_id = ?
    """, (threat_level, priority_score, id))

    # Calculate new Alert message
    msg = 'Monitor'
    if threat_level == 'CRITICAL':
        msg = 'CRITICAL THREAT'
    elif threat_level == 'HIGH':
        msg = 'High threat detected'

    cur.execute("""
        UPDATE Alerts
        SET message = ?, created_at = CURRENT_TIMESTAMP
        WHERE object_id = ?
    """, (msg, id))

    conn.commit()
    conn.close()

    return redirect("/defencepage")


if __name__ == "__main__":
    setup_database()
    app.run(debug=True)