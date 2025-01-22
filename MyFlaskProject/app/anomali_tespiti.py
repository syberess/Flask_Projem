import pandas as pd
from pymongo import MongoClient
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sklearn.ensemble import IsolationForest

# MongoDB bağlantı bilgileri
MONGO_DB_CONFIG = {
    "host": "mongodb+srv://esma:87654321@cluster0.enozu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    "dene_veri_db": "dene_veri",  # Veri eklemek için kullanılacak veritabanı
    "fintech_db": "fintech_db",  # Kullanıcı bilgilerini alacağımız veritabanı
    "veri_dene_collection": "veri_dene",  # veri_dene koleksiyonu
    "users_collection": "users"  # Kullanıcılar koleksiyonu
}

# E-posta bilgileri
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_SENDER = 'fintechuygulamamiz@gmail.com'
EMAIL_PASSWORD = 'chwk ncpm dkmf vqaq'


def get_mongo_client():
    """MongoDB'ye bağlanır ve bağlantıyı döndürür."""
    return MongoClient(MONGO_DB_CONFIG['host'])


def send_email(to_email, subject, body):
    """E-posta gönderme fonksiyonu"""
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
    """MongoDB'den CustomerID'ye göre kullanıcının e-posta bilgisini alır."""
    try:
        # 'fintech_db' veritabanına bağlan
        client = get_mongo_client()
        db = client[MONGO_DB_CONFIG['fintech_db']]  # Kullanıcı bilgilerini alacağımız veritabanı
        users_collection = db[MONGO_DB_CONFIG['users_collection']]  # 'users' koleksiyonu

        # customer_id'yi sorguya gönderiyoruz
        result = users_collection.find_one({"customer_id": str(customer_id)})

        if result:
            return result['email']  # 'email' alanını döndürüyoruz
        else:
            print(f"CustomerID {customer_id} için e-posta bulunamadı.")
            return None
    except Exception as e:
        print(f"Veritabanı hatası: {e}")


def check_anomaly(transaction_date, amount, customer_id):
    """IsolationForest ile harcama anomali tespiti"""
    try:
        # MongoDB verisini çekelim
        client = get_mongo_client()
        db = client[MONGO_DB_CONFIG['dene_veri_db']]  # 'dene_veri' veritabanı
        collection = db[MONGO_DB_CONFIG['veri_dene_collection']]  # 'veri_dene' koleksiyonu



        # MongoDB sorgusu: customer_id ve tarih aralığına göre veri filtreleme
        filtered_data = collection.find({
            "customer_id": customer_id,

        })

        # Veriyi DataFrame'e dönüştürelim
        retail_df = pd.DataFrame(list(filtered_data))

        print(retail_df)

        # 'amount' sütununu alalım
        amounts = retail_df[['amount']]

        # Anomali tespiti için IsolationForest kullanma
        if len(amounts) > 1:
            model = IsolationForest(contamination=0.05)  # %5'lik anomali oranı
            model.fit(amounts)  # Modeli verilerle eğitiyoruz

            # Anomalik veriyi tespit et
            retail_df['anomaly'] = model.predict(amounts)
            print(retail_df[['amount', 'anomaly']])

            # Anomali tespit edildiyse (label: -1)
            if retail_df.loc[retail_df['amount'] == amount, 'anomaly'].values[0] == -1:
                return True

    except Exception as e:
        print(f"Anomali tespiti sırasında hata oluştu: {e}")

    return False


def insert_data(transaction_id, card_holder_name, amount, transaction_date, customer_id, category, payment_method,
                location, store_name):
    """MongoDB'ye veri ekleme ve anomali kontrolü"""
    try:
        # 'dene_veri' koleksiyonuna veri ekleyeceğiz
        client = get_mongo_client()
        db = client[MONGO_DB_CONFIG['dene_veri_db']]  # 'dene_veri' koleksiyonunu kullanmak için
        collection = db[MONGO_DB_CONFIG['veri_dene_collection']]  # 'veri_dene' koleksiyonu

        # Yeni veriyi MongoDB'ye ekleyelim
        new_data = {
            'transaction_id': transaction_id,
            'card_holder_name': card_holder_name,
            'amount': amount,
            'transaction_date': pd.to_datetime(transaction_date),
            'customer_id': customer_id,
            'category': category,
            'payment_method': payment_method,
            'location': location,
            'store_name': store_name  # Store name alanı da ekleniyor
        }

        collection.insert_one(new_data)  # Yeni veri ekleniyor

        print("Yeni veri MongoDB'ye başarıyla eklendi.")

        # Kullanıcının e-posta adresini al
        user_email = get_user_email(customer_id)

        if user_email:
            # Anomali tespiti
            is_anomaly = check_anomaly(transaction_date, amount, customer_id)

            if is_anomaly:
                print(f"Anomali tespit edildi: {amount} dolar, {transaction_date} tarihinde.")
                # Kullanıcıya e-posta gönder
                send_email(user_email, 'Harcama Anomali Bildirimi',
                           f'Yeni bir harcama anomali tespit edildi. Harcama detayları: {amount} dolar harcandı, {transaction_date}.')
            else:
                print("Harcama anomali değil.")
        else:
            print("E-posta adresi alınamadı.")
    except Exception as e:
        print(f"Veri eklenirken hata oluştu: {e}")


def main():
    # Test için örnek veriler
    transaction_id = '10640'
    card_holder_name = 'Aylmar Dunklee'
    amount = 10000
    transaction_date = '12/8/2020'
    customer_id = 40  # Kullanıcının CustomerID'si
    category = 'clothing'
    payment_method = 'credit card'
    location = '687 Annamark Terrace'
    store_name = 'Heba'  # Yeni eklenecek store_name

    # Veritabanına veri ekleyin ve anomaliyi kontrol edin
    insert_data(transaction_id, card_holder_name, amount, transaction_date, customer_id, category, payment_method,
                location, store_name)


# Main fonksiyonunu çağır
if __name__ == '__main__':
    main()
