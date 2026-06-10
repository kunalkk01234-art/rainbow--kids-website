from flask import Flask, render_template, request, redirect, session, send_file
from openpyxl import Workbook
import sqlite3

app = Flask(__name__)
app.secret_key = "rainbowkids2025"

# Create database table
conn = sqlite3.connect("admissions.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS admissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    parent_name TEXT,
    phone TEXT,
    email TEXT,
    class_name TEXT,
    message TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS notices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    notice TEXT
)
""")

conn.commit()
conn.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/admission", methods=["POST"])
def admission():

    student_name = request.form["student_name"]
    parent_name = request.form["parent_name"]
    phone = request.form["phone"]
    email = request.form["email"]
    class_name = request.form["class_name"]
    message = request.form["message"]

    conn = sqlite3.connect("admissions.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO admissions
    (student_name, parent_name, phone, email, class_name, message)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        student_name,
        parent_name,
        phone,
        email,
        class_name,
        message
    ))

    conn.commit()
    conn.close()

    return """
    <h1>Thank You!</h1>
    <p>Your admission inquiry has been submitted successfully.</p>
    <a href="/">Go Back</a>
    """

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "RKPS@2026#Admin":
            session["logged_in"] = True
            return redirect("/admin")

        return "Invalid Login"

    return render_template("login.html")
   
@app.route("/add_notice", methods=["GET", "POST"])
def add_notice():

    if not session.get("logged_in"):
        return redirect("/login")

    if request.method == "POST":

        notice = request.form["notice"]

        conn = sqlite3.connect("admissions.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO notices (notice) VALUES (?)",
            (notice,)
        )

        conn.commit()
        conn.close()

        return redirect("/admin")

    return """
    <h2>Add Notice</h2>

    <form method='POST'>
        <textarea name='notice' rows='5' cols='50'></textarea>
        <br><br>
        <button type='submit'>Add Notice</button>
    </form>
    """
  
    
@app.route("/admin")
def admin():

    if not session.get("logged_in"):
        return redirect("/login")

    conn = sqlite3.connect("admissions.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
    id,
    student_name,
    parent_name,
    phone,
    email,
    class_name,
    message
    FROM admissions
    """)
    data = cursor.fetchall()

    cursor.execute("SELECT id, notice FROM notices")
    notices = cursor.fetchall()

    conn.close()

    html = """
<h1>Rainbow Kids Play School Admissions</h1>

<a href='/add_notice'><button>Add Notice</button></a>
<a href='/export'><button>Export Excel</button></a>
<a href='/logout'><button>Logout</button></a>

<br><br>

<h2>Notices</h2>
"""

    for notice in notices:
        html += f"""
        <div style='border:1px solid #ccc;padding:10px;margin:5px;'>
            {notice[1]}
        </div>
        """

    html += """
    <table border='1' cellpadding='10'>
    <tr>
        <th>ID</th>
        <th>Student</th>
        <th>Parent</th>
        <th>Phone</th>
        <th>Email</th>
        <th>Class</th>
        <th>Message</th>
    </tr>
    """

    for row in data:
        html += f"""
        <tr>
            <td>{row[0]}</td>
            <td>{row[1]}</td>
            <td>{row[2]}</td>
            <td>{row[3]}</td>
            <td>{row[4]}</td>
            <td>{row[5]}</td>
            <td>{row[6]}</td>
        </tr>
        """

    html += "</table>"

    return html

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")
@app.route("/export")
def export_excel():

    if not session.get("logged_in"):
        return redirect("/login")

    conn = sqlite3.connect("admissions.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
    student_name,
    parent_name,
    phone,
    email,
    class_name,
    message
    FROM admissions
    """)

    data = cursor.fetchall()

    conn.close()

    wb = Workbook()
    ws = wb.active

    ws.title = "Admissions"

    ws.append([
        "Student Name",
        "Parent Name",
        "Phone",
        "Email",
        "Class",
        "Message"
    ])

    for row in data:
        ws.append(row)

    file_name = "Admissions.xlsx"

    wb.save(file_name)

    return send_file(
        file_name,
        as_attachment=True
    )
if __name__ == "__main__":
    app.run(debug=True)



