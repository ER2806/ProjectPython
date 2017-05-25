import requests
import redminelib


class main_error(Exception):
    def __init__(self, user_txt=None, logger_txt=None, exception=None):
        self.user_txt = user_txt
        self.logger_txt = logger_txt

        if exception:
            # print(str(exception))
            if isinstance(exception, requests.exceptions.ConnectionError):
                if self.user_txt is None:
                    self.user_txt = str(exception)
                if self.logger_txt is None:
                    self.logger_txt = str(exception)

            elif isinstance(exception, redminelib.exceptions.ResourceNotFoundError):
                if self.user_txt is None:
                    self.user_txt = str(exception)
                if self.logger_txt is None:
                    self.logger_txt = str(exception)

            elif isinstance(exception, redminelib.exceptions.AuthError):
                if self.user_txt is None:
                    self.user_txt = str(exception)
                if self.logger_txt is None:
                    self.logger_txt = str(exception)

            elif isinstance(exception, redminelib.exceptions.ValidationError):
                if self.user_txt is None:
                    self.user_txt = str(exception)
                if self.logger_txt is None:
                    self.logger_txt = str(exception)

            elif isinstance(exception, redminelib.exceptions.ForbiddenError):
                if self.user_txt is None:
                    self.user_txt = str(exception)
                if self.logger_txt is None:
                    self.logger_txt = str(exception)

            else:
                if "HTTPConnectionPool" in str(exception):
                    self.user_txt = "Connection Error"
                    self.logger_txt = "Connection Error"
                else:
                    self.user_txt = str(exception)
                    self.logger_txt = str(exception)

    def __str__(self):
        return self.user_txt

    def to_log(self):
        return self.logger_txt
