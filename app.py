from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
app = Flask(__name__)
app.secret_key = 'super_secret_threat_key'
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
        session['username'] = request.form.get('username')
        session['role'] = request.form.get('rank')
        return redirect("/defencepage")
    return render_template("login.html")

@app.route("/defencepage/login/create", methods=["GET", "POST"])
def create_user():
    if request.method == "POST":
        username = request.form.get("username")
        passwd = request.form.get("passwd")
        role = request.form.get("role")
        access_key = request.form.get("access_key")
        
        if access_key != "maverick21":
            flash("INVALID ACCESS KEY")
            return redirect("/defencepage/login/create")
            
        conn = get_conn()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO Users (username, password, role) VALUES (?, ?, ?)", (username, passwd, role))
        except sqlite3.IntegrityError:
            flash("USER ALREADY EXISTS")
            return redirect("/defencepage/login/create")
        finally:
            conn.commit()
            conn.close()
            
        return redirect("/defencepage/login")
        
    return render_template("register.html")

@app.route("/defencepage")
def index():
    if 'role' not in session:
        return redirect("/defencepage/login")
    conn = get_conn()
    cur = conn.cursor()

    alerts = cur.execute("SELECT * FROM Alerts ORDER BY created_at DESC").fetchall()
    threats = cur.execute("SELECT * FROM Threat_Assessment ORDER BY assessed_at DESC").fetchall()
    audit_logs = cur.execute("SELECT * FROM Audit_Log ORDER BY timestamp DESC LIMIT 50").fetchall()
    aerial_objects = cur.execute("SELECT * FROM Aerial_Objects ORDER BY detected_at DESC").fetchall()

    conn.close()

    return render_template(
        "index.html",
        alerts=alerts,
        threats=threats,
        audit_logs=audit_logs,
        aerial_objects=aerial_objects
    )
@app.route("/defencepage/dbs")
def view_database():
    if 'role' not in session:
        return redirect("/defencepage/login")
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = cur.fetchall()
    
    db_data = {}
    for (table_name,) in tables:
        cur.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cur.fetchall()]
        
        cur.execute(f"SELECT * FROM {table_name}")
        rows = cur.fetchall()
        
        db_data[table_name] = {'columns': columns, 'rows': rows}
        
    conn.close()
    return render_template("dbs.html", db_data=db_data)


@app.route("/defencepage/add", methods=["POST"])
def add():
    if session.get('role') not in ['general', 'commander']:
        flash("UNAUTHORIZED: Clearance level insufficient to add targets.")
        return redirect("/defencepage")
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
    if session.get('role') != 'general':
        flash("UNAUTHORIZED: Only GENERAL rank can delete records.")
        return redirect("/defencepage")
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
    if session.get('role') not in ['general', 'commander']:
        flash("UNAUTHORIZED: Clearance level insufficient to edit targets.")
        return redirect("/defencepage")
    conn = get_conn()
    cur = conn.cursor()
    obj = cur.execute("SELECT * FROM Aerial_Objects WHERE object_id = ?", (id,)).fetchone()
    conn.close()
    if not obj:
        return redirect("/defencepage")
    return render_template("edit.html", obj=obj)


@app.route("/defencepage/update/<int:id>", methods=["POST"])
def update(id):
    if session.get('role') not in ['general', 'commander']:
        flash("UNAUTHORIZED: Clearance level insufficient to update targets.")
        return redirect("/defencepage")
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