import uuid
import json
from flask.sessions import (SessionMixin, SessionInterface)
from itsdangerous import  Signer, BadSignature,want_bytes
class MySession(dict, SessionMixin):
    def __init__(self, initial=None, sessionId=None):  # '__int__' yerine '__init__' olmalı
        self.initial = initial
        self.sessionId = sessionId
        super(MySession, self).__init__(initial or {})

    def __setitem__(self, key, value):
        super(MySession, self).__setitem__(key, value)

    def __getitem__(self, item):
        return super(MySession, self).__getitem__(item)

    def __delitem__(self, key):
        super(MySession, self).__delitem__(key)


class MySessionInterface(SessionInterface):
    session_class =MySession
    salt = 'my_session'
    container= dict() #bir sözlük oluşturduk buraya kaydedilecek

    def __init__(self):
        pass

    def open_session(self, app, request):
        # Flask'ta session cookie name 'session' olarak ayarlandığı için app.config['SESSION_COOKIE_NAME'] kullanılmalı
        signedsessionId = request.cookies.get(app.config.get('SESSION_COOKIE_NAME', 'session'))

        if not signedsessionId:  # Eğer session_id yoksa yeni bir tane oluşturur
            sessionId = str(uuid.uuid4())
            return self.session_class(sessionId=sessionId)

        signer = Signer(app.secret_key, salt=self.salt, key_derivation='hmac')
        try:
            sessionId = signer.unsign(signedsessionId).decode()
        except BadSignature:
            sessionId = str(uuid.uuid4())
            return self.session_class(sessionId=sessionId)

        initialSessionValueAsJson = self.container.get(sessionId)  # Sözlükten değeri alır
        try:
            initialSessionValue = json.loads(initialSessionValueAsJson)  # JSON'u sözlüğe çevirir
        except:
            sessionId = str(uuid.uuid4())
            return self.session_class(sessionId=sessionId)

        return self.session_class(initialSessionValue, sessionId=sessionId)

    def save_session(self, app, session, response):
        sessionAsJson = json.dumps(dict(session))
        self.container[session.sessionId] = sessionAsJson  # Session'ı container'a kaydeder

        signer = Signer(app.secret_key, salt=self.salt, key_derivation='hmac')
        signedSessionId = signer.sign(want_bytes(session.sessionId))
        signedSessionId = signedSessionId.decode('utf-8') # Bayt'ı metin formatına çevir

        response.set_cookie(app.config.get('SESSION_COOKIE_NAME', 'session'), signedSessionId)
