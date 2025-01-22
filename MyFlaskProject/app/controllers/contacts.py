from app.models import ContactRequest
from app.models.contact_request import contact_collection


# İletişim isteklerini getiren fonksiyon
def GetContactList():
    contacts = contact_collection.find()  # MongoDB'den tüm kayıtları al
    return [[contact.get("name"), contact.get("category"), contact.get("priority")] for contact in contacts]

# Yeni bir iletişim isteği kaydetmek için fonksiyon
def SaveContactRequest(name, email, category, priority, message):
    contact_request = ContactRequest(name, email, category, priority, message)
    contact_request.Save()
    print(contact_request)