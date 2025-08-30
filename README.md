🔐 Anormal Harcama Tespiti ile Finansal Güvenlik (TÜBİTAK 2209-A Destekli Proje)

Bu proje, TÜBİTAK 2209-A kapsamında desteklenen bir araştırma projesidir.
Amaç, bireylerin finansal harcamalarında anormal davranışları (fraud/dolandırıcılık ihtimali taşıyan işlemleri) tespit ederek finansal güvenliği artıran bir yapay zeka sistemi geliştirmektir.

Proje Flask tabanlı bir web uygulaması olarak geliştirilmiştir. Kullanıcılar, sisteme harcama verilerini girdiğinde model bu verileri analiz eder, anomali olasılığı taşıyan işlemleri işaretler ve kullanıcıya anında e-mail bildirimi gönderir.

📌 Özellikler

Anomali Tespiti:

Isolation Forest

Z-Score yöntemi

Web Arayüzü (Flask):

Kullanıcı dostu arayüz

Dinamik sonuç görselleştirme

Veri Görselleştirme: Harcama dağılımları ve anormal noktaların grafiksel gösterimi

Gerçek Zamanlı Çalışma: Kullanıcı girişine karşı anında analiz

📧 E-mail Bildirimi:

Anormal harcama tespit edildiğinde kullanıcıya otomatik e-mail gönderilir

Bildirim, şüpheli işlem detaylarını içerir

🛠 Kullanılan Teknolojiler

Python 3.0

Flask (Backend framework)

Scikit-Learn (Isolation Forest, Z-Score)

Pandas & NumPy (Veri işleme)

Matplotlib & Seaborn (Veri görselleştirme)

SMTP (Flask-Mail) – Anlık e-mail gönderimi

📂 Proje Yapısı
Flask_Projem/
│
├── app.py               # Ana Flask uygulaması
├── models/              # Anomali tespit algoritmaları
│   ├── isolation_forest.py
│   └── zscore.py
├── utils/               # Bildirim ve yardımcı fonksiyonlar
│   └── mail_service.py  # Flask-Mail ile e-mail gönderimi
├── static/              # CSS, görseller
├── templates/           # HTML şablonları (Jinja2)
│   └── index.html
├── data/                # Örnek harcama veri setleri
└── README.md            # Proje açıklaması

▶️ Kurulum ve Çalıştırma

Depoyu klonla

git clone https://github.com/syberess/Flask_Projem.git
cd Flask_Projem


Bağımlılıkları yükle

pip install -r requirements.txt


Mail yapılandırmasını ayarla
.env dosyası oluştur ve aşağıdaki bilgileri gir:

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seninmail@gmail.com
MAIL_PASSWORD=uygulama_sifresi


Uygulamayı çalıştır

python app.py


Tarayıcıdan aç:
👉 http://127.0.0.1:5000/

📊 Çalışma Mantığı

Kullanıcı sisteme harcama verilerini girer.

Model verileri Isolation Forest ve Z-Score yöntemleriyle analiz eder.

Şüpheli harcama bulunursa:

Arayüzde işaretlenir

Kullanıcıya anında e-mail bildirimi gönderilir

Kullanıcı raporunu hem ekrandan hem e-mail üzerinden takip edebilir.

🎯 Proje Katkısı

FinTech sektöründe bireysel ve kurumsal kullanıcılar için dolandırıcılık tespitine katkı sağlar.

Akademik araştırma niteliği taşıyan ve TÜBİTAK tarafından desteklenen bir projedir.

Anlık bildirim mekanizması ile kullanıcıların finansal güvenliğini artırır.

👨‍💻 Yazarlar

Rümeysa Yıldırım

Esma Polat
