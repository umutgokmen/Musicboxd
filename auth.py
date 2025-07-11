from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask import current_app as app
from werkzeug.security import check_password_hash, generate_password_hash

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)
        cur = app.mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        app.mysql.connection.commit()
        cur.close()
        flash("Kayıt başarılı! Giriş yapabilirsiniz.")
        return redirect(url_for("auth.login"))
    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        cur = app.mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cur.fetchone()
        cur.close()
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            # Kullanıcı adı admin ise admin haklarını ver
            session["is_admin"] = (user["username"] == "admin")
            if user.get("is_admin", 0):
                return redirect(url_for("admin.admin_panel"))
            else:
                return redirect(url_for("song.song_list"))
        else:
            flash("Kullanıcı adı veya şifre yanlış!")
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))