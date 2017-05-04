import requests
import redminelib


class main_error(Exception):
    def __init__(self, user_txt=None, logger_txt=None, exception=None):
        self.user_txt = user_txt
        self.logger_txt = logger_txt

        if exception:
            if isinstance(exception, requests.exceptions.ConnectionError):
                self.user_txt = ""
                self.logger_txt = ""

            elif isinstance(exception, redminelib.exceptions.ResourceNotFoundError):
                self.user_txt = "Hello"
                self.logger_txt = "Hello"

            elif isinstance(exception, redminelib.exceptions.AuthError):
                self.user_txt = ""
                self.logger_txt = ""

            elif isinstance(exception, redminelib.exceptions.ValidationError):
                self.user_txt = ""
                self.logger_txt = ""

            elif isinstance(exception, redminelib.exceptions.ForbiddenError):
                self.user_txt = ""
                self.logger_txt = ""

            else:
                self.user_txt = str(exception)
                self.logger_txt = str(exception)

    def __str__(self):
        return self.user_txt

    def to_log(self):
        return self.logger_txt
