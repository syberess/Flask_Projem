from flask import session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash


client = MongoClient("mongodb+srv://esma:87654321@cluster0.enozu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

db = client['fintech_db']  # Veritabanı adı
users_collection = db['users']


def UserLogin(username, password):
    # Kullanıcıyı username ile bul
    user = db.users.find_one({"username": username})

    # Kullanıcı varsa ve şifre doğruysa
    if user and check_password_hash(user["password"], password):
        # Oturum açma işlemi
        session["username"] = username
        session["customer_id"] = user["customer_id"]  # customer_id'yi ekliyoruz
        session["email"] = user["email"]  # email'i ekliyoruz
        return True
    return False



def UserLogout():
    if "username" in session:
        # Kullanıcıyı ve customer_id'yi, email'i session'dan sil
        del session["username"]
        del session["customer_id"]
        del session["email"]
        return True
    else:
        return False


def UserRegister(username, password, customer_id, email):
    hashed_password = generate_password_hash(password)  # Şifreyi hashleyin
    user_data = {
        "username": username,
        "password": hashed_password,
        "customer_id": customer_id,
        "email": email  # email bilgisini de ekliyoruz
    }
    db.users.insert_one(user_data)  # Kullanıcıyı veritabanına ekleyin
    return True


def GetCurrentUsername():
    username = ""
    customer_id = None
    email = ""
    loginAuth = False
    if "username" in session and "customer_id" in session and "email" in session:
        username = session["username"]
        customer_id = session["customer_id"]
        email = session["email"]
        loginAuth = True

    return username, customer_id, email, loginAuth  # email'i de döndürüyoruz


