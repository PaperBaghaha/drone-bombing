from flask import Flask, render_template, request, redirect, session
import sqlite3
from functools import wraps

app = Flask(__name__)
app.secret_key = 'super_secret_terminal_key'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect('/defencepage/login')
        return f(*args, **kwargs)
    return decorated_function

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
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        rank = request.form.get("rank")
        
        conn = get_conn()
        cur = conn.cursor()
        user = cur.execute("SELECT * FROM Users WHERE username = ? AND password = ? AND role = ?", (username, password, rank)).fetchone()
        conn.close()
        
        if user:
            session['username'] = user[1]
            session['role'] = user[3]
            return redirect("/defencepage")
        else:
            error = "UNAUTHORIZED ACCESS ATTEMPT. INVALID CREDENTIALS."
            
    return render_template("login.html", error=error)

@app.route("/defencepage/logout")
def logout():
    session.clear()
    return redirect("/defencepage/login")

@app.route("/defencepage/login/createuser", methods=["GET", "POST"])
def createuser():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        rank = request.form.get("rank")
        passkey = request.form.get("passkey")
        
        if passkey == "maverick21":
            conn = get_conn()
            cur = conn.cursor()
            try:
                cur.execute("INSERT INTO Users (username, password, role) VALUES (?, ?, ?)", (username, password, rank))
                conn.commit()
                return redirect("/defencepage/login")
            except sqlite3.IntegrityError:
                error = "ERROR: OPERATIVE ID ALREADY IN DATABASE."
            finally:
                conn.close()
        else:
            error = "UNAUTHORIZED ACCESS: INVALID MILITARY PASS KEY."
            
    return render_template("createuser.html", error=error)

@app.route("/defencepage")
@login_required
def index():
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
@login_required
def view_database():
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name != 'Users';")
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
@login_required
def add():
    if session.get('role') == 'analyst':
        flash('ACCESS DENIED: Analysts are restricted to view-only access.', 'error')
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
@login_required
def delete_record(id):
    role = session.get('role')
    if role in ['analyst', 'commander']:
        flash('ACCESS DENIED: Only Generals have authorization to delete records.', 'error')
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
@login_required
def edit(id):
    if session.get('role') == 'analyst':
        flash('ACCESS DENIED: Analysts are restricted to view-only access.', 'error')
        return redirect("/defencepage")
        
    conn = get_conn()
    cur = conn.cursor()
    obj = cur.execute("SELECT * FROM Aerial_Objects WHERE object_id = ?", (id,)).fetchone()
    conn.close()
    if not obj:
        return redirect("/defencepage")
    return render_template("edit.html", obj=obj)


@app.route("/defencepage/update/<int:id>", methods=["POST"])
@login_required
def update(id):
    if session.get('role') == 'analyst':
        flash('ACCESS DENIED: Analysts are restricted to view-only access.', 'error')
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