from random import random
from random import randint


from flask import Flask, render_template, session, request ,url_for,redirect
from pymongo import MongoClient
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
import base64
from sklearn.ensemble import IsolationForest
from .controllers import MySessionInterface
from .views import home, contacts, users
from flask import Flask, render_template, request, redirect, flash, session
from pymongo import MongoClient
from datetime import datetime
import pandas as pd
from sklearn.ensemble import IsolationForest
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_pyfile("config.py")
    app.session_interface = MySessionInterface()

    if app.config["VERSION"] == "1.0.1":
        pass
    elif app.config["VERSION"] == "1.0.2":
        pass

    app.register_blueprint(home.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(contacts.bp)

    @app.route("/history", methods=["GET", "POST"])
    def history():
        if "customer_id" not in session:
            return redirect(url_for("users.Login"))

        customer_id = session["customer_id"]
        print(f"Customer ID: {customer_id}")

        # MongoDB bağlantısı
        client = MongoClient(
            "mongodb+srv://esma:87654321@cluster0.enozu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        db = client["dene_veri"]
        collection = db["veri_dene"]

        # Veri çekme
        user_data = pd.DataFrame(list(collection.find({"customer_id": int(customer_id)})))
        print("Çekilen veri:", user_data)

        if user_data.empty:
            print("Müşteri için veri bulunamadı.")
            flash("Geçmiş harcamalar bulunamadı.", "info")
            return render_template("history.html", username=session.get("username", "Kullanıcı"), history=[])

        if 'transaction_date' in user_data.columns:
            user_data['transaction_date'] = pd.to_datetime(user_data['transaction_date'], errors='coerce')
            user_data['transaction_date'] = user_data['transaction_date'].fillna(pd.Timestamp.now())
        else:
            print("transaction_date sütunu bulunamadı!")

        # Tarih ve ürün adı filtreleme
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        product_name = request.args.get("product_name")

        if start_date:
            user_data = user_data[user_data['transaction_date'] >= pd.to_datetime(start_date)]
        if end_date:
            user_data = user_data[user_data['transaction_date'] <= pd.to_datetime(end_date)]
        if product_name:
            user_data = user_data[user_data['category'].str.contains(product_name, case=False, na=False)]

        # Tablo verisi için liste oluştur
        history_records = user_data[
            ['transaction_date', 'store_name', 'amount', 'category', 'payment_method', 'location']].to_dict(
            orient='records')
        print("History Records:", history_records)

        return render_template("history.html", username=session.get("username", "Kullanıcı"), history=history_records)

    # Route to display customer spending data and graphics
    @app.route('/customer_spending/<int:customer_id>')
    def customer_spending(customer_id):
        # MongoDB bağlantısı ve veri çekme
        client = MongoClient(
            "mongodb+srv://esma:87654321@cluster0.enozu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        )
        db = client["dene_veri"]  # Veritabanı adı
        collection = db["veri_dene"]  # Koleksiyon adı

        data = collection.find({"customer_id": customer_id})
        user_data = pd.DataFrame(list(data))

        # Kullanıcı adını al
        username = session.get("username", "Guest")  # Varsayılan olarak "Guest"

        # Toplam harcama ve ortalama işlem hesapla
        total_spending = user_data['amount'].sum()
        average_transaction = user_data['amount'].mean()

        # Anomali tespiti için IsolationForest kullan
        amounts = user_data[['amount']].values
        model = IsolationForest(contamination=0.05)  # Verilerin %5'inin anomali olarak kabul edilmesi
        user_data['anomaly'] = model.fit_predict(amounts)

        # transaction_date'yi datetime formatına dönüştür
        user_data['transaction_date'] = pd.to_datetime(user_data['transaction_date'], errors='coerce')

        # NaT (Not a Time) olan verileri, boş değer olarak işle
        user_data['transaction_date'] = user_data['transaction_date'].apply(
            lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else 'Invalid Date')

        # Anomali tespit grafiği oluştur
        anomaly_data = user_data[user_data['anomaly'] == -1]  # -1 anomaliyi gösterir
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.scatter(user_data['transaction_date'], user_data['amount'], color='blue', label='Normal')
        ax.scatter(anomaly_data['transaction_date'], anomaly_data['amount'], color='red', label='Anomaly')
        ax.set_title(f"Customer {customer_id} - Anomaly Detection")
        ax.set_xlabel('Transaction Date')
        ax.set_ylabel('Amount (USD)')
        ax.legend()
        img_anomaly = BytesIO()
        plt.savefig(img_anomaly, format='png')
        img_anomaly.seek(0)
        graphs = {}
        graphs['anomaly_detection'] = base64.b64encode(img_anomaly.getvalue()).decode('utf-8')

        # 1. Kategoriye göre harcama pasta grafiği
        category_distribution = user_data.groupby('category')['amount'].sum()
        fig, ax = plt.subplots(figsize=(8, 8))
        category_distribution.plot(kind='pie', autopct='%1.1f%%', startangle=90, cmap='tab20', ax=ax)
        ax.set_title(f"Customer {customer_id} - Spending by Category")
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        graphs['category_pie'] = base64.b64encode(img.getvalue()).decode('utf-8')

        # 2. Ülkeye göre harcama bar grafiği
        country_spending = user_data.groupby('billing_country')['amount'].sum().sort_values(ascending=False).head(10)
        fig, ax = plt.subplots(figsize=(12, 6))
        country_spending.plot(kind='bar', color='teal', alpha=0.8, ax=ax)
        ax.set_title(f"Customer {customer_id} - Spending by Country")
        ax.set_xlabel('Country')
        ax.set_ylabel('Total Spending (USD)')
        ax.set_xticklabels(country_spending.index, rotation=45)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        img2 = BytesIO()
        plt.savefig(img2, format='png')
        img2.seek(0)
        graphs['country_bar'] = base64.b64encode(img2.getvalue()).decode('utf-8')

        # 3. Ödeme yöntemine göre harcama pasta grafiği
        payment_distribution = user_data.groupby('payment_method')['amount'].sum()
        fig, ax = plt.subplots(figsize=(8, 8))
        payment_distribution.plot(kind='pie', autopct='%1.1f%%', startangle=90, cmap='tab20', ax=ax)
        ax.set_title(f"Customer {customer_id} - Spending by Payment Method")
        img3 = BytesIO()
        plt.savefig(img3, format='png')
        img3.seek(0)
        graphs['payment_pie'] = base64.b64encode(img3.getvalue()).decode('utf-8')

        # 4. En yüksek ve en düşük harcama yapılan kategoriler bar grafiği
        category_spending = user_data.groupby('category')['amount'].sum()
        top_categories = category_spending.nlargest(5)
        bottom_categories = category_spending.nsmallest(5)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(top_categories.index, top_categories.values, color='green', alpha=0.7, label='Highest')
        ax.bar(bottom_categories.index, bottom_categories.values, color='red', alpha=0.7, label='Lowest')
        ax.set_title(f"Customer {customer_id} - Highest and Lowest Spending Categories")
        ax.set_xlabel('Category')
        ax.set_ylabel('Total Spending (USD)')
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        img4 = BytesIO()
        plt.savefig(img4, format='png')
        img4.seek(0)
        graphs['category_bar'] = base64.b64encode(img4.getvalue()).decode('utf-8')

        # 5. Günlük harcama trendi çizgi grafiği
        user_data['transaction_date'] = pd.to_datetime(user_data['transaction_date'], format='%Y-%m-%d',
                                                       errors='coerce')
        daily_spending = user_data.groupby('transaction_date')['amount'].sum()
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(daily_spending.index, daily_spending.values, marker='o', linestyle='-', color='b')
        ax.set_title(f"Customer {customer_id} - Daily Spending Trend", fontsize=14)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Spending (USD)', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.6)
        img5 = BytesIO()
        plt.savefig(img5, format='png')
        img5.seek(0)
        graphs['daily_trend'] = base64.b64encode(img5.getvalue()).decode('utf-8')

        # Send graphics to HTML template along with total spending and average transaction
        return render_template('customer_spending.html',
                               graphs=graphs,
                               customer_id=customer_id,
                               username=username,  # Send the username to the template
                               total_spending=total_spending,
                               average_transaction=average_transaction)

    # MongoDB bağlantı bilgileri
    MONGO_DB_CONFIG = {
        "host": "mongodb+srv://esma:87654321@cluster0.enozu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
        "dene_veri_db": "dene_veri",
        "fintech_db": "fintech_db",
        "veri_dene_collection": "veri_dene",
        "users_collection": "users"
    }

    # E-posta bilgileri
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    EMAIL_SENDER = 'fintechuygulamamiz@gmail.com'
    EMAIL_PASSWORD = 'chwk ncpm dkmf vqaq'

    def get_mongo_client():
        return MongoClient(MONGO_DB_CONFIG['host'])

    def send_email(to_email, subject, body):
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.sendmail(EMAIL_SENDER, to_email, msg.as_string())
                print("E-posta başarıyla gönderildi.")
        except Exception as e:
            print(f"E-posta gönderilirken hata oluştu: {e}")

    def get_user_email(customer_id):
        try:
            client = get_mongo_client()
            db = client[MONGO_DB_CONFIG['fintech_db']]
            users_collection = db[MONGO_DB_CONFIG['users_collection']]
            result = users_collection.find_one({"customer_id": str(customer_id)})
            return result['email'] if result else None
        except Exception as e:
            print(f"Veritabanı hatası: {e}")

    def check_anomaly(transaction_date, amount, customer_id):
        try:
            client = get_mongo_client()
            db = client[MONGO_DB_CONFIG['dene_veri_db']]
            collection = db[MONGO_DB_CONFIG['veri_dene_collection']]
            filtered_data = collection.find({"customer_id": customer_id})
            retail_df = pd.DataFrame(list(filtered_data))

            if not retail_df.empty:
                amounts = retail_df[['amount']]
                model = IsolationForest(contamination=0.05)
                model.fit(amounts)
                retail_df['anomaly'] = model.predict(amounts)

                if retail_df.loc[retail_df['amount'] == amount, 'anomaly'].values[0] == -1:
                    return True
        except Exception as e:
            print(f"Anomali tespiti sırasında hata oluştu: {e}")
        return False

    @app.route('/submit', methods=['GET', 'POST'])
    def submit():
        if request.method == 'GET':
            return render_template('form.html')

        if 'customer_id' not in session:
            return redirect(url_for('users.Login'))

        try:
            # Oturum Kontrolü
            if 'customer_id' not in session:
                session['customer_id'] = request.form.get('customer_id')
            if 'username' not in session:
                session['username'] = request.form.get('username')

            # Formdan Gelen Veriler
            transaction_id = randint(20000, 30000)
            card_holder_name = session['username']
            amount = float(request.form['amount'])
            transaction_date = datetime.now()
            customer_id = int(session['customer_id'])  # customer_id integer olarak saklanıyor
            category = request.form['category']
            payment_method = request.form['payment_method']
            location = request.form['location']
            store_name = request.form['store_name']

            # Veri Doğrulama
            if not all([card_holder_name, amount, category, payment_method, location, store_name]):
                flash("Eksik veya hatalı veri gönderildi.", "danger")
                return redirect('/submit')

            # Yeni Veri Hazırlığı
            new_data = {
                'transaction_id': transaction_id,
                'card_holder_name': card_holder_name,
                'amount': amount,
                'transaction_date': transaction_date.isoformat(),  # ISO formatına dönüştürme
                'customer_id': customer_id,  # customer_id integer olarak saklanıyor
                'category': category,
                'payment_method': payment_method,
                'location': location,
                'store_name': store_name
            }

            # MongoDB'ye Veri Ekleme
            client = get_mongo_client()
            db = client[MONGO_DB_CONFIG['dene_veri_db']]
            collection = db[MONGO_DB_CONFIG['veri_dene_collection']]

            print(f"MongoDB'ye eklenecek veri: {new_data}")
            collection.insert_one(new_data)
            print("Veri başarıyla MongoDB'ye eklendi.")
            flash("Veri başarıyla kaydedildi.", "success")

            # Kullanıcı E-posta İşlemleri
            user_email = get_user_email(customer_id)
            if user_email:
                is_anomaly = check_anomaly(transaction_date, amount, customer_id)
                if is_anomaly:
                    print("Anomali tespit edildi.")
                    send_email(user_email, 'Harcama Anomali Bildirimi',
                               f'Yeni bir harcama anomali tespit edildi. Harcama detayları: {amount} dolar, {transaction_date}.')
                    flash("Anomali tespit edildi ve kullanıcıya e-posta gönderildi.", "warning")
                else:
                    print("Anomali tespit edilmedi.")
                    flash("Anomali tespit edilmedi.", "info")
            else:
                print("E-posta adresi bulunamadı.")
                flash("Kullanıcının e-posta adresi bulunamadı.", "danger")

        except Exception as e:
            print(f"Bir hata oluştu: {e}")
            flash(f"Bir hata oluştu: {e}", "danger")

        return redirect('/submit')

    @app.route("/user_home")
    def user_home():
        if "customer_id" not in session:
            return redirect(url_for("users.Login"))

        return render_template(
            "user_home.html",
            username=session.get("username", "Kullanıcı")
        )

    return app
