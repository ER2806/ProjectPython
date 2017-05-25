class Credent:

    def __init__(self):
        self.login = None
        self.password = None

    def set_login(self, new_login):
        self.login = str(new_login)

    def set_password(self, new_pwd):
        self.password = str(new_pwd)

    def clean(self):
        self.login = None
        self.password = None

    def get_login(self):
        return self.login

    def get_password(self):
        return self.password



class Project:

    def __init__(self, name=None,  description=None, identifier=None, is_public=None):
        self.name = name
        self.description = description
        self.identifier = identifier
        self.is_public = is_public

    def set_name(self, new_name):
        self.name = str(new_name)

    def set_description(self, new_description):
        self.description = str(new_description)

    def set_identifier(self, new_identifier):
        self.identifier = str(new_identifier)

    def set_ispublic(self, new_ispublic):
        self.is_public = bool(new_ispublic)

    def clean(self):
        self.name = None
        self.description = None
        self.identifier = None
        self.is_public = None



class Issue:

    def set_project_id(self, new_project_id):
        self.project_id = str(new_project_id)

    def set_subject(self, new_subject):
        self.subject = str(new_subject)

    def set_description(self, new_description):
        self.description = str(new_description)

    def set_tracker_id(self, new_tracker_id):
        self.tracker_id = int(new_tracker_id)

    def set_status_id(self, new_status_id):
        self.status_id = int(new_status_id)

    def set_priority_id(self, new_priority_id):
        self.priority_id = int(new_priority_id)

    def clean(self):
        self.project_id = None
        self.priority_id = None
        self.description = None
        self.tracker_id = None
        self.status_id = None
