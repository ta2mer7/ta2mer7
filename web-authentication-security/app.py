from flask import Flask, render_template, request, redirect, session, g, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import requests

app = Flask(__name__)

# ================= SETTINGS =================

app.secret_key = "x9F!2kL#8pQ@1sZ7"

DATABASE = "database.db"
UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ================= DATABASE =================

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    db.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        is_admin INTEGER DEFAULT 0
    )
    """)

    db.execute("""
    CREATE TABLE IF NOT EXISTS logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        action TEXT
    )
    """)

    db.commit()


with app.app_context():
    init_db()

# ================= TRANSLATIONS =================

translations = {

    "en": {

        "home": "Home",
        "login": "Login",
        "register": "Register",
        "logout": "Logout",
        "dashboard": "Dashboard",
        "scan_file": "Scan File",
        "scan_url": "Scan URL",
        "admin": "Admin",

        "welcome_title": "Secure Your Digital World",

        "welcome_text":
        "Advanced cyber security platform for monitoring threats, scanning suspicious links, analyzing uploaded files, and protecting systems in real time.",

        "start_now": "Get Started",
        "create_account": "Create Account",

        "username": "Username",
        "password": "Password",

        "upload_file": "Upload File",
        "choose_file": "Choose File",

        "scan_link": "Scan Link",

        "safe": "Looks Safe",
        "danger": "Dangerous Content",

        "wrong_login": "Wrong username or password",
        "user_exists": "Username already exists"

    },

    "ar": {

        "home": "الرئيسية",
        "login": "تسجيل الدخول",
        "register": "إنشاء حساب",
        "logout": "تسجيل خروج",
        "dashboard": "لوحة التحكم",
        "scan_file": "فحص ملف",
        "scan_url": "فحص رابط",
        "admin": "الإدارة",

        "welcome_title": "قم بحماية عالمك الرقمي",

        "welcome_text":
        "منصة أمن سيبراني متقدمة لمراقبة التهديدات وفحص الروابط وتحليل الملفات وحماية النظام بشكل مباشر.",

        "start_now": "ابدأ الآن",
        "create_account": "إنشاء حساب",

        "username": "اسم المستخدم",
        "password": "كلمة المرور",

        "upload_file": "رفع ملف",
        "choose_file": "اختر ملف",

        "scan_link": "فحص رابط",

        "safe": "يبدو آمناً",
        "danger": "محتوى خطير",

        "wrong_login": "اسم المستخدم أو كلمة المرور خاطئة",
        "user_exists": "المستخدم موجود مسبقاً"

    }
}


def get_lang():
    return session.get("lang", "en")


@app.route("/toggle_lang")
def toggle_lang():

    if get_lang() == "en":
        session["lang"] = "ar"
    else:
        session["lang"] = "en"

    return redirect(request.referrer or "/")

# ================= LANDING PAGE =================

@app.route("/")
def landing():

    if "user" in session:
        return redirect("/dashboard")

    return render_template(
        "landing.html",
        t=translations[get_lang()],
        lang=get_lang()
    )

# ================= LOGIN =================

@app.route("/login", methods=["GET", "POST"])
def login():

    if "user" in session:
        return redirect("/dashboard")

    error = None

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        db = get_db()

        user = db.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()

        if user and check_password_hash(user["password"], password):

            session["user"] = username
            session["is_admin"] = user["is_admin"]

            db.execute(
                "INSERT INTO logs(username,action) VALUES(?,?)",
                (username, "login success")
            )

            db.commit()

            return redirect("/dashboard")

        else:

            db.execute(
                "INSERT INTO logs(username,action) VALUES(?,?)",
                (username, "login failed")
            )

            db.commit()

            error = translations[get_lang()]["wrong_login"]

    return render_template(
        "login.html",
        error=error,
        t=translations[get_lang()],
        lang=get_lang()
    )

# ================= REGISTER =================

@app.route("/register", methods=["GET", "POST"])
def register():

    if "user" in session:
        return redirect("/dashboard")

    error = None

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        db = get_db()

        try:

            db.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",
                (
                    username,
                    generate_password_hash(password)
                )
            )

            db.execute(
                "INSERT INTO logs(username,action) VALUES(?,?)",
                (username, "registered")
            )

            db.commit()

            return redirect("/login")

        except sqlite3.IntegrityError:

            error = translations[get_lang()]["user_exists"]

    return render_template(
        "register.html",
        error=error,
        t=translations[get_lang()],
        lang=get_lang()
    )

# ================= LOGOUT =================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

# ================= DASHBOARD =================

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        user=session["user"],
        t=translations[get_lang()],
        lang=get_lang()
    )

# ================= FILE SCAN =================

@app.route("/upload", methods=["GET", "POST"])
def upload():

    if "user" not in session:
        return redirect("/login")

    result = None

    if request.method == "POST":

        file = request.files.get("file")

        if file and file.filename != "":

            path = os.path.join(
                UPLOAD_FOLDER,
                file.filename
            )

            file.save(path)

            try:

                content = open(
                    path,
                    encoding="utf-8",
                    errors="ignore"
                ).read().lower()

                score = 0

                if "<script>alert" in content:
                    score += 3

                if "eval(" in content:
                    score += 2

                if "document.cookie" in content:
                    score += 3

                if score >= 5:
                    result = "⚠️ Dangerous File"
                else:
                    result = "✅ File Looks Safe"

            except:
                result = "✅ File Uploaded"

    return render_template(
        "upload.html",
        result=result,
        t=translations[get_lang()],
        lang=get_lang()
    )

# ================= URL SCAN =================

@app.route("/scan_url", methods=["GET", "POST"])
def scan_url():

    if "user" not in session:
        return redirect("/login")

    result = None

    if request.method == "POST":

        url = request.form.get("url")

        try:

            response = requests.get(url, timeout=5)

            content = response.text.lower()

            score = 0

            if "<script>alert" in content:
                score += 3

            if "document.cookie" in content:
                score += 3

            if "eval(" in content:
                score += 2

            if score >= 5:
                result = "⚠️ High Risk Website"
            else:
                result = "✅ Looks Safe"

        except:
            result = "❌ Invalid URL"

    return render_template(
        "scan_url.html",
        result=result,
        t=translations[get_lang()],
        lang=get_lang()
    )

# ================= ADMIN =================

@app.route("/admin")
def admin():

    if "user" not in session:
        return redirect("/login")

    if not session.get("is_admin"):
        return redirect("/dashboard")

    db = get_db()

    logs = db.execute(
        "SELECT * FROM logs ORDER BY id DESC"
    ).fetchall()

    return render_template(
        "admin.html",
        logs=logs,
        t=translations[get_lang()],
        lang=get_lang()
    )

# ================= API =================

@app.route("/api/stats")
def stats():

    db = get_db()

    users = db.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]

    success = db.execute(
        "SELECT COUNT(*) FROM logs WHERE action='login success'"
    ).fetchone()[0]

    failed = db.execute(
        "SELECT COUNT(*) FROM logs WHERE action='login failed'"
    ).fetchone()[0]

    return jsonify(
        users=users,
        success=success,
        failed=failed
    )

# ================= RUN =================

if __name__ == "__main__":
    app.run(debug=True)