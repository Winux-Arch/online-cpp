from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import subprocess
from datetime import datetime
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
import tempfile
import shutil

app = Flask(__name__)
app.secret_key = "supersecretkey"

def get_db_connection():
    return psycopg2.connect(
        dbname="coding_platform",
        user="postgres",
        password="postgres",
        host="localhost",  # Change from 'db' to 'localhost'
        port=5432  # Default PostgreSQL port
    )

@app.route("/")
def index():
    if "user_id" in session:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, title, end_date FROM tasks WHERE end_date > NOW() ORDER BY end_date")
        tasks = cur.fetchall()
        cur.close()
        conn.close()
        return render_template("index.html", tasks=tasks)
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, password FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user and check_password_hash(user[1], password):
            session["user_id"] = user[0]
            return redirect(url_for("index"))
        flash("Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

@app.route("/upload/<int:task_id>", methods=["GET", "POST"])
def upload(task_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, end_date FROM tasks WHERE id = %s", (task_id,))
    task = cur.fetchone()
    cur.close()
    conn.close()

    if not task or task[2] < datetime.now():
        flash("Task is closed for submissions.")
        return redirect(url_for("index"))

    if request.method == "POST":
        file = request.files["code"]
        if file:
            filename = f"user_{session['user_id']}_task_{task_id}.cpp"
            filepath = os.path.join("submissions", filename)
            file.save(filepath)

            # Compile and test code
            test_result = subprocess.run(
                ["g++", filepath, "-o", "submission.out"],
                capture_output=True,
                text=True
            )

            if test_result.returncode != 0:
                result = test_result.stderr
            else:
                result = subprocess.run(
                    ["./test_task.sh", str(task_id), "submission.out"],
                    capture_output=True,
                    text=True
                ).stdout

            # Save result in the database
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO results (user_id, task_id, result) VALUES (%s, %s, %s)",
                (session["user_id"], task_id, result)
            )
            conn.commit()
            cur.close()
            conn.close()
            flash("Submission processed.")
        return redirect(url_for("index"))

    return render_template("upload.html", task=task)

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
        WHERE results.user_id = %s
    """, (session["user_id"],))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("results.html", results=results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
