from flask import request, redirect, url_for, render_template, Blueprint, flash
from app.controllers import SaveContactRequest, GetCurrentUsername, GetContactList
from app.models.contact_request import contact_collection

bp =Blueprint("contacts", __name__, template_folder="../templates")

@bp.route("/contact", methods=["GET", "POST"])
def Contact():
    if request.method == "POST":
        if request.form:
            name = request.form.get("name")
            email = request.form.get("email")
            category = request.form.get("category")
            priority = request.form.get("priority")
            message = request.form.get("message")

            # Form doğrulama
            if not all([name, email, category, priority, message]):
                flash("Lütfen tüm alanları doldurun!", "error")
                return redirect(url_for("contacts.Contact"))

            # İletişim isteğini kaydet
            SaveContactRequest(name, email, category, priority, message)
            flash("Mesajınız başarıyla gönderildi!", "success")
            return redirect(url_for("contacts.Contact"))

    # Sadece ihtiyacınız olan değerleri alın
    username, _, _, loginAuth = GetCurrentUsername()
    return render_template("contact.html", username=username, login_auth=loginAuth)


@bp.route("/list")
def ContactList():
    username, _, _, loginAuth = GetCurrentUsername()
    try:
        contactList = GetContactList()
        print("MongoDB'den çekilen iletişim listesi:", contactList)  # Verileri loglayın
    except Exception as e:
        print(f"Hata oluştu: {e}")
        contactList = []

    # contactList'in doğru gönderildiğinden emin olun
    return render_template("contact_list.html", username=username, login_auth=loginAuth, contactList=contactList)
