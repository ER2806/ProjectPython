import requests
import redmine as redm
from redmine import exceptions


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


class RedmineProject:
    def __init__(self, url):
        self.URL = url
        self.redmine = redm.Redmine(url)
        # self.user = user

    def set_url(self, url):
        self.URL = url
        self.redmine = redm.Redmine(url)

    def create_new_project(self, user, name, identifier=None, description=None, homepage=None, is_public=True, parent_id=None, inherit_members=True):

        if user.key is None:
            return False

        if identifier is None:
            identifier = name

        try:
            redm.Redmine(self.URL, key=user.key).auth()
        except exceptions.AuthError as error:
            raise error

        redmine_proj = redm.Redmine(self.URL, key=user.key)
        project = redmine_proj.project.new()
        project.name = name
        project.identifier = identifier
        project.description = description
        project.homepage = homepage
        project.is_public = is_public
        project.parent_id = parent_id
        project.inherit_members = inherit_members
        try:
            project.save()
        except exceptions.ValidationError as error:
            raise error

        except requests.exceptions.ConnectionError as error:
            raise error

        except exceptions.ResourceNotFoundError as err:
            raise err

        return True

    def delete_project(self, user, project_id):
        if user.key is None:
            return False

        try:
            redm.Redmine(self.URL, key=user.key).auth()
        except exceptions.AuthError as error:
            raise error

        redmine_proj = redm.Redmine(self.URL, key=user.key)

        try:
            redmine_proj.project.delete(project_id)

        except requests.exceptions.ConnectionError as error:
            raise error

        except exceptions.ResourceNotFoundError as error:
            raise error

        except exceptions.ForbiddenError as error:
            raise error

        return True


    def get_all_projects(self):
        try:
            return list(self.redmine.project.all())

        except requests.exceptions.ConnectionError as err:
            raise err

        except exceptions.ResourceNotFoundError as err:
            raise err

    # Возвращает проект по id или по идентификатору
    def get_project_params_by_project_id(self, project_id):
        """"""
        try:
            return self.redmine.project.get(project_id)

        except requests.exceptions.ConnectionError as error:
            raise error

        except exceptions.ResourceNotFoundError as error:
            raise error

    # Возвращает список проектов в которых участвует пользователь
    def get_only_any_user_projects(self, user):
        # В случае, если не определены id пользователя
        if user.username is None and user.key is None:
            return None

        try:
            if user.key is not None:
                user_redmine = redm.Redmine(self.URL, key=user.key).auth()

            else:
                user_redmine = redm.Redmine(self.URL, username=user.username, password=user.password).auth()

            user_projects = []
            all_projects = self.redmine.project.all()
            for project in all_projects:
                for membership in project.memberships:
                    if 'user' in dir(membership):
                        if membership.user.id == user_redmine.id:
                            user_projects.append(project)

            return user_projects

        except requests.exceptions.ConnectionError as error:
            raise error

        except exceptions.ResourceNotFoundError as error:
            raise error

        except exceptions.AuthError as error:
            raise error

    # Проект должен задаваться либо по id, либо по индентиикатору
    # param - str
    # Может принимать: 'created_on', 'id', 'identifier', 'is_public', 'name', 'status'
    #                   'time_entries', 'trackers'
    def get_any_project_param(self, project_id, param):
        try:
            _project = self.redmine.project.get(project_id)
            return _project[param]

        except requests.exceptions.ConnectionError as error:
            raise error

        except exceptions.ResourceNotFoundError as error:
            raise error


class Issue:
    def __init__(self, redmine):
        self.redmine = redmine

    def set_redmine(self, redmine):
        self.redmine = redmine

    def create_new_issue(self, user,  project_id, subject, description=None, tracker_id=None, status_id=1, priority_id=1, is_private=False, assigned_to_id=None, whatcher_user_ids=None, parent_issue_id=None,
                         done_ratio=0):
        if priority_id > 5:
            priority_id = 1

        if self.redmine.username is None:
            self.redmine.username = user.username
            self.redmine.password = user.password

        try:
            issue = self.redmine.issue.new()
            issue.project_id = project_id
            issue.subject = subject
            issue.description = description
            issue.status_id = status_id
            issue.priority_id = priority_id
            issue.done_ratio = done_ratio
            issue.is_private = is_private
            issue.assigned_to_id = assigned_to_id
            issue.whatcher_user_ids = whatcher_user_ids or []
            issue.parent_issue_id = parent_issue_id
            issue.tracker_id = tracker_id
            issue.save()

        except requests.exceptions.ConnectionError as error:
            raise error

        except exceptions.ResourceNotFoundError as error:
            raise error

    def change_issue_status(self, issue_id, new_status_id):
        # statud_id: 1 - New, 2 - In Progress 3 - Resolved
        #            4 - FeedBack 5 - Closed 6 - FeedBack
        if new_status_id > 6:
            return False

        try:
            issue = self.redmine.issue.get(issue_id)
            issue.status_id = new_status_id
            issue.save()

        except requests.exceptions.ConnectionError as error:
            raise error
        except exceptions.ResourceNotFoundError as error:
            raise error

    def change_issue_priority(self, issue_id, new_priority_id):
        # statud_id: 1 - New, 2 - In Progress 3 - Resolved
        #            4 - FeedBack 5 - Closed 6 - FeedBack
        if new_priority_id > 5:
            return False

        try:
            issue = self.redmine.issue.get(issue_id)
            issue.priority_id = new_priority_id
            issue.save()

        except requests.exceptions.ConnectionError as error:
            raise error

        except exceptions.ResourceNotFoundError as error:
            raise error

    def delete_issue(self, issue_id):
        try:
            self.redmine.issue.delete(issue_id)

        except requests.exceptions.ConnectionError as error:
            raise error

        except exceptions.ResourceNotFoundError as error:
            raise error

        except exceptions.ForbiddenError as error:
            raise error

    def get_all_issue(self):
        try:
            return list(self.redmine.issue.all())

        except requests.exceptions.ConnectionError as error:
            raise error

        except exceptions.ResourceNotFoundError as error:
            raise error

    def get_all_issue_from_any_project(self, proj_id):
        try:
            return list(self.redmine.issue.filter(project_id=proj_id))

        except requests.exceptions.ConnectionError as error:
            raise error

        except exceptions.ResourceNotFoundError as error:
            raise error

    def get_any_issue_param(self, issue_id, param):
        try:
            issue = self.redmine.issue.get(issue_id)
            return issue[param]

        except requests.exceptions.ConnectionError as error:
            raise error

        except exceptions.ResourceNotFoundError as error:
            raise error


