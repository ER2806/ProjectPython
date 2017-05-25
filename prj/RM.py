import requests
import redminelib as redm
import general_except
from redminelib import exceptions


#  Create string by object project
def project_to_line(project):
    statuses = ['Active', '2', '3', '4', 'Closed']
    result = '\u25B6 Project: {}\n    \u25E6 Identifier: {}\n    \u25E6 Id: {}\n    \u25E6 Status: {}\n' \
             '    \u25E6 Public: {}\n    \u25E6 Created: {}\n    \u25E6 Updated: {}' \
             ''.format(str(project.name), str(project.identifier), str(project.id),
                       statuses[(project.status - 1) % 5], str(project.is_public),
                       str(project.created_on), str(project.updated_on))

    return result


#   Generate new list of project to list of strings
#   for smart view
def list_porjects_to_list_lines(projects):
    result = []
    for project in projects:
        result.append(project_to_line(project))
        # print(result)
    new_res = ["\n\n".join(result)]
    return new_res


def issue_to_line(issue):
    result = '\u25B6 Issue subject: {}\n    \u25cf Description: {}\n    \u25cf Id: {}\n    \u25cf Tracker: {}\n' \
             '    \u25cf Author: {}\n    \u25cf Project: {}\n    \u25cf Priority: {}\n    \u25cf Status: {}\n' \
             '    \u25cf Started: {}\n    \u25cf Created: {}\n    \u25cf Updated: {}\n' \
             ''.format(str(issue.subject), str(issue.description), str(issue.id), str(issue.tracker),
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

        ''''
        self.username = 'qudusov98'
        self.password = '904310001'
        '''

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

        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError, BaseException) as error:
            raise general_except.main_error(exception=error)

        return True

    # Return user Api_Key
    def get_api_key(self, url):
        try:
            user_redmine = redm.Redmine(url, username=self.username, password=self.password).auth()
            return user_redmine.api_key

        except (exceptions.AuthError, exceptions.ResourceNotFoundError, requests.exceptions.ConnectionError, BaseException) as error:
            raise general_except.main_error(exception=error)


class RedmineProject:
    def __init__(self, url):
        self.URL = url
        self.redmine = redm.Redmine(url)
    # self.user = user

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

            except (exceptions.AuthError, BaseException) as error:
                raise general_except.main_error(exception=error)

        if identifier is None:
            identifier = name

        try:
            redm.Redmine(self.URL, key=user.key).auth()
        except (exceptions.AuthError, BaseException) as error:
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
        except (exceptions.ValidationError, requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError, BaseException) as error:
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

            except (exceptions.AuthError, BaseException) as error:
                raise general_except.main_error(exception=error)

        try:
            redm.Redmine(self.URL, key=user.key).auth()
        except (exceptions.AuthError, BaseException) as error:
            raise general_except.main_error(exception=error)

        redmine_proj = redm.Redmine(self.URL, key=user.key)

        try:
            redmine_proj.project.delete(project_id)

        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError, exceptions.ForbiddenError, BaseException) as error:
            raise general_except.main_error(exception=error)

        return True

    # def set_user(self, user):
    #     self.user = user
    # Возвращает список со всеми проектами
    def __get_all_projects(self):
        try:
            return list(self.redmine.project.all())

        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError, BaseException) as error:
            raise general_except.main_error(exception=error)

    # Return list of strings with all projects
    # for sending in telebot
    def get_all_projects(self):
        try:
            return list_porjects_to_list_lines(self.__get_all_projects())

        except (general_except.main_error, BaseException) as error:
            raise error

    def is_valid_project_id(self, project_id):
        try:
            self.redmine.project.get(project_id)
        except requests.exceptions.ConnectionError as error:
            print('requests')
            raise general_except.main_error(exception=error)
        except exceptions.ResourceNotFoundError:
            return False

        except BaseException as error:
            raise general_except.main_error(exception=error)

        return True

    # returns project by id or idents
    def __get_project_params_by_project_id(self, project_id):
        try:
            proj = list()
            proj.append(self.redmine.project.get(project_id))
            return proj
        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError, BaseException) as error:
            raise general_except.main_error(exception=error)

    # Returns project by id or indent in one string
    # for smart send in TBot
    def get_project_params_by_project_id(self, project_id):
        try:
            return list_porjects_to_list_lines(self.__get_project_params_by_project_id(project_id))

        except (general_except.main_error, BaseException) as error:
            raise error

    # Returns list of user projects
    def __get_only_any_user_projects(self, user):
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

        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError, exceptions.AuthError, BaseException) as error:
            raise general_except.main_error(exception=error)

    def get_only_any_user_projects(self, user):
        try:
            return list_porjects_to_list_lines(self.__get_only_any_user_projects(user))

        except (general_except.main_error, BaseException) as error:
            raise error

    def get_any_project_param(self, project_id, param):
        try:
            _project = self.redmine.project.get(project_id)
            return _project[param]

        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError, BaseException) as error:
            raise general_except.main_error(exception=error)


class Issue:
    # def __init__(self, redmine):
    #     self.redmine = redmine
    def __init__(self, url, user):
        self.url = url
        self.redmine = redm.Redmine(url, username=user.username, password=user.password)
        self.user = user

    def set_redmine(self, redmine):
        self.redmine = redmine

    def set_url(self, url):
        self.url = url
        self.redmine = redm.Redmine(url, username=self.user.username, password=self.user.password)

    def set_user(self, user):
        self.user = user
        if self.url is not None:
            self.redmine = redm.Redmine(self.url, username=self.user.username, password=self.user.password)

    def create_new_issue(self, user,  project_id, subject, description=None, tracker_id=1, status_id=1, priority_id=1, is_private=False, assigned_to_id=None, whatcher_user_ids=None, parent_issue_id=None,
                         done_ratio=0):
        # tracker_is : 1 - Bug, 2 - Feature, 3 - Support
        # status_id: 1-New, 2-In Progress, 3 - Resolved, 4 - FeedBack, 5 - Closed, 6 - Rejected
        # priority_id 1 - Low, 2 - Normal, 3 - High, 4 - Urgent, 5 - Immidiate
        if priority_id > 5:
            priority_id = 1

        if user.username is not None:
            try:
                user.key = user.get_api_key(self.url)

            except (exceptions.AuthError, BaseException) as error:
                raise general_except.main_error(exception=error)
        else:
            raise general_except.main_error(user_txt='username is empty', logger_txt='username is empty')

        self.redmine = redm.Redmine(self.url, key=user.key)

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

        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError, BaseException) as error:
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
        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError, BaseException) as error:
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
        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError, BaseException) as error:
            raise general_except.main_error(exception=error)
        return True

    def delete_issue(self, issue_id):
        try:
            self.redmine.issue.delete(issue_id)

        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError, exceptions.ForbiddenError, BaseException) as error:
            raise general_except.main_error(exception=error)

    def __get_all_bugs(self, project_id=None):
        try:
            if project_id is None:
                return list(self.redmine.issue.filter(tracker_id=1))
            else:
                return list(self.redmine.issue.filter(tracker_id=1, project_id=project_id))

        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError, BaseException) as error:
            raise general_except.main_error(exception=error)

    def get_all_bugs(self, project_id=None):
        try:
            return list_issues_to_list_lines(self.__get_all_bugs(project_id=project_id))

        except (general_except.main_error, BaseException) as error:
            raise error

    def __get_all_features(self, project_id=None):
        try:
            if project_id is None:
                return list(self.redmine.issue.filter(tracker_id=2))
            else:
                return list(self.redmine.issue.filter(tracker_id=2, project_id=project_id))

        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError, BaseException) as error:
            raise general_except.main_error(exception=error)

    def get_all_features(self, project_id=None):
        try:
            return list_issues_to_list_lines(self.__get_all_features(project_id=project_id))
        except (general_except.main_error, BaseException) as error:
            raise error

    def __get_all_supports(self, project_id=None):
        try:
            if project_id is None:
                return list(self.redmine.issue.filter(tracker_id=3))
            else:
                return list(self.redmine.issue.filter(tracker_id=3, project_id=project_id))

        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError, BaseException) as error:
            raise general_except.main_error(exception=error)

    def get_all_supports(self, project_id=None):
        try:
            return list_issues_to_list_lines(self.__get_all_supports(project_id=project_id))
        except (general_except.main_error, BaseException) as error:
            raise error

    def __get_all_issue(self):
        try:
            return list(self.redmine.issue.all())

        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError, BaseException) as error:
            raise general_except.main_error(exception=error)

    def get_all_issue(self):
        try:
            return list_issues_to_list_lines(self.__get_all_issue())
        except (general_except.main_error, BaseException) as error:
            raise error

    def _get_all_issue_from_any_project(self, proj_id):
        try:
            return list(self.redmine.issue.filter(project_id=proj_id))

        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError, exceptions.AuthError, BaseException) as error:
                raise general_except.main_error(exception=error)

    def get_all_issue_from_any_project(self, project_id):
        try:
            return list_issues_to_list_lines(self._get_all_issue_from_any_project(project_id))
        except (general_except.main_error, BaseException) as error:
            raise error

    def __get_issue_by_issue_id(self, issue_id):
        try:
            result = []
            issue = (self.redmine.issue.get(issue_id))
            result.append(issue)
            return result
            # return list((self.redmine.issue.filter(issue_id=issue_id)))

        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError, BaseException) as error:
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

        except (requests.exceptions.ConnectionError, exceptions.ResourceNotFoundError, BaseException) as error:
            raise general_except.main_error(exception=error)


# if __name__ == '__main__':
#     URL1 = 'http://localhost:8080/redmine'
#     redmine1 = redm.Redmine(URL1, username='qudusov98', password='904310001')
#     my_user = User(username='qudusov98', password='904310001')
#     new_user = User(username='danil', password='12345678')
#     # print(new_user.is_valid_user(URL1))
#     redmine_class = RedmineProject(URL1)
#
#     try:
#         redmine_class.create_new_project(user=new_user, name='project_by_me', identifier='he', description='lalalalla', is_public=True)
#     except general_except.main_error as ex:
#         print(str(ex))
#     all_projs = redmine_class.get_all_projects()
#     for proj in all_projs:
#         print(proj)
#         print('\n')
#     my_projs = redmine_class.get_only_any_user_projects(new_user)
#     for proj in my_projs:
#         print(proj)
#
#     try:
#         issue_class = Issue(url=URL1, user=new_user)
#         issue_class.delete_issue(40)
#         iss1 = issue_class.get_issue_by_issue_id(5)
#         iss1 = issue_class.get_all_issue_from_any_project('project200')
#         for i in iss1:
#             print(i)
#         bugs = issue_class.get_all_bugs()
#         for bug in bugs:
#            print(bug)
#         issue_class.change_issue_priority(issue_id=74, new_priority_id=3)
#         issue_class.create_new_issue(user=my_user, project_id='danil_project', subject='my_issue', description='all_good')
#
#     except general_except.main_error as ex:
#         print(ex.__str__())
#
#
#     iss2 = issue_class.get_all_issue_from_any_project(3)
#     for i in iss2:
#         print(i)
#     issue_class.create_new_issue(user=my_user, project_id=4, subject='Hello', description='hahahah')
#     print(dir(redmine1))
#     print(redmine1.username)
