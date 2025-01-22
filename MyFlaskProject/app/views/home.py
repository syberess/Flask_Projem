from flask import render_template, Blueprint
from app.controllers import GetCurrentUsername

bp =Blueprint("home", __name__, template_folder="../templates")

@bp.route("/")
def Index():
    # Hata mesajına göre, fonksiyonun döndürdüğü değeri dört parça halinde almanız gerekebilir:
    username, customer_id, email, loginAuth = GetCurrentUsername()

    return render_template("index.html", username=username, login_auth=loginAuth, customer_id=customer_id)




