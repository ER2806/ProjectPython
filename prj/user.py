class User:
    def __init__(self, api_key=None,  username=None, password=None):
        self.key = api_key
        self.username = username
        self.password = password

    def set_login(self, new_name):
        self.username = new_name

    def set_password(self, new_pass):
        self.password = new_pass

    def set_key(self, api_key):
        self.key = api_key

    # Проверка на авторизацию юзера
    def is_valid_user(self, url):
        try:
            redm.Redmine(url, username=self.username, password=self.password).auth()

        except exceptions.AuthError:
            return False

        except requests.exceptions.ConnectionError as error:
            raise error

        except exceptions.ResourceNotFoundError as error:
            raise error

        return True

    # Возвращает Api_Key юзера
    def get_api_key(self, url):
        try:
            user_redmine = redm.Redmine(url, username=self.username, password=self.password).auth()
            return user_redmine.api_key

        except (exceptions.AuthError, exceptions.ResourceNotFoundError, requests.exceptions.ConnectionError) as error:
            raise error
