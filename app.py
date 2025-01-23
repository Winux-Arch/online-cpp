from flask import Flask, render_template, request, redirect, url_for, session
import os
import subprocess
from datetime import datetime
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import tempfile
import shutil

app = Flask(__name__)
app.secret_key = "e9b2b4af6f0ffd5e40b70b36316ea24b8db071d3f4650f08906ea9a23039b8ee"

# SQLite database connection
def get_db_connection():
    conn = sqlite3.connect("coding_platform.db")  # SQLite database file
    conn.row_factory = sqlite3.Row  # To fetch rows as dictionaries
    return conn

@app.route("/")
def index():
    if "user_id" in session:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, title, end_date, assignment FROM tasks WHERE end_date > ? ORDER BY end_date", (datetime.now(),))
        tasks = cur.fetchall()
        cur.close()
        conn.close()
        return render_template("index.html", tasks=tasks)
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    result=None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user and check_password_hash((user[1]), password):
            session["user_id"] = user[0]
            return redirect(url_for("index"))
        result="Invalid credentials"
    return render_template("login.html",result=result)

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

@app.route("/upload/<int:task_id>", methods=["GET", "POST"])
def upload(task_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    res = False

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, end_date FROM tasks WHERE id = ?", (task_id,))
    task = cur.fetchone()
    cur.close()
    conn.close()

    if not task or datetime.fromisoformat(task["end_date"]) < datetime.now():
        res = True

    if request.method == "POST":
        file = request.files["code"]
        if file:
            filename = f"user_{session['user_id']}_task_{task_id}.cpp"
            filepath = os.path.join("submissions", filename)
            file.save(filepath)

            result = subprocess.run(
                ["python3", "test_runner.py", str(task_id), filename],
                capture_output=True,
                text=True
            ).stdout

            # Save result in the database
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO results (user_id, task_id, result) VALUES (?, ?, ?)",
                (session["user_id"], task_id, result)
            )
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for("results"))

    return render_template("upload.html", task=task,res=res)

@app.route("/results")
def results():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT tasks.title, results.result
        FROM results
        INNER JOIN tasks ON results.task_id = tasks.id
        WHERE results.user_id = ?
    """, (session["user_id"],))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("results.html", results=results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
