class Credent():
    def __init__(self):
        self.login = ''
        self.password = ''
    def set_login(self, login):
        self.login = str(login)
    def set_password(self, pwd):
        self.password = str(pwd)
    def clean(self):
        self.login = ""
        self.password = ""
    def get_login(self):
        return self.login
    def get_password(self):
        return self.password

