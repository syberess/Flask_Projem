from pymongo import MongoClient

# MongoDB bağlantısını kur
client = MongoClient("mongodb+srv://esma:87654321@cluster0.enozu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['fintech_db']  # Veritabanı adı
contact_collection = db['contacts']  # Koleksiyon adı

# ContactRequest sınıfı
class ContactRequest:
    def __init__(self, name, email, category, priority, message):
        self.name = name
        self.email = email
        self.category = category
        self.priority = priority
        self.message = message

    def __str__(self):
        return (f"name:{self.name} email:{self.email} category:{self.category} "
                f"priority:{self.priority} message:{self.message}")

    def Save(self):
        # MongoDB'ye iletişim isteğini kaydet
        contact_collection.insert_one({
            "name": self.name,
            "email": self.email,
            "category": self.category,
            "priority": self.priority,
            "message": self.message
        })