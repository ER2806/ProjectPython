class Credent():
    def __init__(self):
        self.data = []
    def setLogin(self, login):
        self.data.append(str(login))
    def setPassword(self, pwd):
        self.data.append(str(pwd))
    def get(self):
        data = self.data
        self.data = []
        return data
