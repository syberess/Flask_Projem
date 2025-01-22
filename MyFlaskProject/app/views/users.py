from flask import request, redirect, url_for, render_template, Blueprint
from app.controllers import UserLogin, GetCurrentUsername, UserLogout
from app.controllers import UserRegister

bp = Blueprint("users", __name__, template_folder="../templates")

@bp.route("/login", methods=["GET", "POST"])
def Login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return render_template("login.html", error="Tüm alanlar zorunludur.")  # Hata mesajı ekleyebilirsiniz

        if UserLogin(username, password):  # Yalnızca username ve password ile doğrulama yapılacak
            return redirect(url_for("user_home"))
        else:
            return render_template("login.html", error="Kullanıcı adı veya şifre hatalı.")

    return render_template("login.html")



@bp.route("/register", methods=["GET", "POST"])
def Register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        customer_id = request.form["customer_id"]  # customer_id alınıyor
        email = request.form["email"]  # Email alınıyor

        if UserRegister(username, password, customer_id, email):  # customer_id ve email kayda ekleniyor
            return redirect(url_for("users.Login"))
        else:
            error = "Bu kullanıcı adı, müşteri ID veya e-posta zaten mevcut."
            return render_template("register.html", error=error)

    return render_template("register.html")


@bp.route("/logout")
def Logout():
    if UserLogout():
        return redirect(url_for("home.Index"))