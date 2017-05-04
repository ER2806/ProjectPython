import requests
import redminelib as redm
import general_except
from redminelib import exceptions


#  Create string by object project
def project_to_line(project):
    result = 'project_name: {}\nidentifier: {}\nid: {}\nstatus: {}\n' \
             'is_public: {}\ncreated_on: {}\nupdated_on{}' \
             ''.format(str(project.name), str(project.identifier), str(project.id),
                       str(project.status), str(project.is_public),
                       str(project.created_on), str(project.updated_on))
    return result


#   Generate new list of project to list of strings
#   for smart view
def list_porjects_to_list_lines(projects):
    result = []
    for project in projects:
        result.append(project_to_line(project))

    return result


def issue_to_line(issue):
    result = 'issue_subject: {}\ndescription: {}\nid: {}\n' \
             'author: {}\nproject: {}\npriority: {}\nstatus: {}\n' \
             'start_date: {}\ncreated_on: {}\nupdated_on: {}\n' \
             ''.format(str(issue.subject), str(issue.description), str(issue.id),
                       str(issue.author), str(issue.project), str(issue.priority),
                       str(issue.status), str(issue.start_date), str(issue.created_on),
                       str(issue.updated_on))

    return result


def list_issues_to_list_lines(issues):
    result = []
    for issue in issues:
        result.append(issue_to_line(issue))

    return result


class User:
    def __init__(self, api_key=None,  username=None, password=None):
        # self.key = api_key
        self.key = api_key
        self.username = username
        self.password = password

    def set_login(self, new_name):
        self.username = new_name

    def set_password(self, new_pass):
        self.password = new_pass

    def set_key(self, api_key):
        self.key = api_key

    # Checking user autorization
    def is_valid_user(self, url):
        try:
            redm.Redmine(url, username=self.username, password=self.password).auth()

        except exceptions.AuthError:
            return False

        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError) as error:
            raise general_except.main_error(exception=error)

        return True

    # Return user Api_Key
    def get_api_key(self, url):
        try:
            user_redmine = redm.Redmine(url, username=self.username, password=self.password).auth()
            return user_redmine.api_key

        except (exceptions.AuthError, exceptions.ResourceNotFoundError, requests.exceptions.ConnectionError) as error:
            raise general_except.main_error(exception=error)


class RedmineProject:
    def __init__(self, url):
        self.URL = url
        self.redmine = redm.Redmine(url)

    def set_url(self, url):
        self.URL = url
        self.redmine = redm.Redmine(url)

    '''
        Returns:
        True if all is ok;
        False - if username и api_key not specified
        else throwing exception
    '''
    def create_new_project(self, user, name, identifier=None, description=None, homepage=None, is_public=True, parent_id=None, inherit_members=True):
        # tracker_ids = [], issue_custom_field_ids=[], custom_fields=[]):

        if user.key is None and user.username is None:
            return False

        elif user.username is not None:
            try:
                user.key = user.get_api_key(self.URL)

            except exceptions.AuthError as error:
                raise general_except.main_error(exception=error)

        if identifier is None:
            identifier = name

        try:
            redm.Redmine(self.URL, key=user.key).auth()
        except exceptions.AuthError as error:
            raise general_except.main_error(exception=error)

        redmine_proj = redm.Redmine(self.URL, key=user.key)
        project = redmine_proj.project.new()
        project.name = name
        project.identifier = identifier
        project.description = description
        project.homepage = homepage
        project.is_public = is_public
        project.parent_id = parent_id
        project.inherit_members = inherit_members
        # project.issue_custom_fields_ids = issue_custom_field_ids
        # project.custom_fields = custom_fields
        try:
            project.save()
        except (exceptions.ValidationError, requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError) as error:
            raise general_except.main_error(exception=error)

        return True


    '''
        Returns:
        True if all is ok;
        False - if username и api_key not specified
        else throwing exception
    '''
    def delete_project(self, user, project_id):
        if user.key is None and user.username is None:
            return False

        elif user.username is not None:
            try:
                user.key = user.get_api_key(self.URL)

            except exceptions.AuthError as error:
                raise general_except.main_error(exception=error)

        try:
            redm.Redmine(self.URL, key=user.key).auth()
        except exceptions.AuthError as error:
            raise general_except.main_error(exception=error)

        redmine_proj = redm.Redmine(self.URL, key=user.key)

        try:
            redmine_proj.project.delete(project_id)

        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError, exceptions.ForbiddenError) as error:
            raise general_except.main_error(exception=error)

        return True

    # def set_user(self, user):
    #     self.user = user
    # Returns list with all project
    def __get_all_projects(self):
        try:
            return list(self.redmine.project.all())

        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError) as error:
            raise general_except.main_error(exception=error)

    # Return list of strings with all projects
    # for sending in telebot
    def get_all_projects(self):
        try:
            return list_porjects_to_list_lines(self.__get_all_projects())

        except general_except.main_error as error:
            raise error

    # returns project by id or idents
    def get_project_params_by_project_id(self, project_id):
        try:
            proj = list()
            proj.append(project_to_line(self.redmine.project.get(project_id)))
            return proj
        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError) as error:
            raise general_except.main_error(exception=error)


    # returns project by id or indent
    def __get_project_params_by_project_id(self, project_id):
        try:
            proj = list()
            proj.append(self.redmine.project.get(project_id))
            return proj
        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError) as error:
            raise general_except.main_error(exception=error)


    # Returns project by id or indent in one string
    # for smart send in TBot
    def get_project_params_by_project_id(self, project_id):
        try:
            return list_porjects_to_list_lines(self.__get_project_params_by_project_id(project_id))

        except general_except.main_error as error:
            raise error


    # Returns list of user projects
    def __get_only_any_user_projects(self, user):
        # If user id is not specified
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

        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError, exceptions.AuthError) as error:
            raise general_except.main_error(exception=error)

    def get_only_any_user_projects(self, user):
        try:
            return list_porjects_to_list_lines(self.__get_only_any_user_projects(user))

        except general_except.main_error as error:
            raise error

    def get_any_project_param(self, project_id, param):
        try:
            _project = self.redmine.project.get(project_id)
            return _project[param]

        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError) as error:
            raise general_except.main_error(exception=error)


class Issue:
    # def __init__(self, redmine):
    #     self.redmine = redmine
    def __init__(self, url=None, user=None):
        self.url = url
        self.redmine = redm.Redmine(url)
        self.user = user

    def set_redmine(self, redmine):
        self.redmine = redmine

    def set_url(self, url):
        self.url = url
        self.redmine = redm.Redmine(url)
        if self.user is not None:
            self.redmine.username = self.user.username
            self.redmine.username = self.user.password

    def set_user(self, user):
        self.user = user
        if self.url is not None:
            self.redmine.username = self.user.username
            self.redmine.password = self.user.password

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

        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError) as error:
            raise general_except.main_error(exception=error)

    def change_issue_status(self, issue_id, new_status_id):
        # statud_id: 1 - New, 2 - In Progress 3 - Resolved
        # 4 - FeedBack 5 - Closed 6 - FeedBack
        if new_status_id > 6:
            return False

        try:
            issue = self.redmine.issue.get(issue_id)
            issue.status_id = new_status_id
            issue.save()
        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError) as error:
                raise general_except.main_error(exception=error)

        return True

    def change_issue_priority(self, issue_id, new_priority_id):
        # statud_id: 1 - New, 2 - In Progress 3 - Resolved
        #            4 - FeedBack 5 - Closed 6 - FeedBack
        if new_priority_id > 5:
            return False

        try:
            issue = self.redmine.issue.get(issue_id)
            issue.priority_id = new_priority_id
            issue.save()
        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError) as error:
            raise general_except.main_error(exception=error)
        return True

    def delete_issue(self, issue_id):
        try:
            self.redmine.issue.delete(issue_id)

        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError, exceptions.ForbiddenError) as error:
            raise general_except.main_error(exception=error)


    def __get_all_issue(self):
        try:
            return list(self.redmine.issue.all())

        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError) as error:
            raise general_except.main_error(exception=error)


    def get_all_issue(self):
        try:
            return list_issues_to_list_lines(self.__get_all_issue())
        except general_except.main_error as error:
            raise error


    def _get_all_issue_from_any_project(self, proj_id):
        try:
            return list(self.redmine.issue.filter(project_id=proj_id))

        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError) as error:
                raise general_except.main_error(exception=error)


    def get_all_issue_from_any_project(self, project_id):
        try:
            return list_issues_to_list_lines(self._get_all_issue_from_any_project(project_id))
        except general_except.main_error as error:
            raise error


    def __get_issue_by_issue_id(self, issue_id):
        try:
            result = []
            issue = (self.redmine.issue.get(issue_id))
            result.append(issue)
            return result
            # return list((self.redmine.issue.filter(issue_id=issue_id)))

        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError) as error:
            raise general_except.main_error(exception=error)


    def get_issue_by_issue_id(self, issue_id):
        try:
            return list_issues_to_list_lines(self.__get_issue_by_issue_id(issue_id))
        except general_except.main_error as error:
            raise error


    def get_any_issue_param(self, issue_id, param):
        try:
            issue = self.redmine.issue.get(issue_id)
            return issue[param]

        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError) as error:
            raise general_except.main_error(exception=error)
