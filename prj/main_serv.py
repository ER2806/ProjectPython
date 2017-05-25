# -*- coding: utf-8 -*-
import telebot
import get_key
import credent
import RM
import logging
import general_except
import sqlite3

ADDRESS = "http://192.168.0.101:8080/redmine"

''' logger '''
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler("log.txt")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

''' data base '''
db_conn = sqlite3.connect("users.db", check_same_thread = False)
db_curs = db_conn.cursor()

# base init

pattern_cred = credent.Credent()
pattern_project = credent.Project()
pattern_iss = credent.Issue()

bot = telebot.TeleBot(str(get_key.get()))


@bot.message_handler(commands=['func'])
def send_func(message):
    bot.send_message(message.chat.id, "List of possible commands:")
    text = '/start or /help - welcome message\n\
            /registration - reg process\n\
            /func - list of possible functions\n\
            /all_prjs - get all projects\n\
            /my_prjs - get your projects\n\
            /prj_params - get project parameters\n\
            /del_prj - delete project\n\
            /all_issue - get all issues\n\
            /prj_issue - get project issues\n\
            /chg_issue_status - change issue status\n\
            /chg_issue_priority - change issue priority\n\
            /del_issue - delete issue'
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['kill'])
def exit(message):
    import sys
    sys.exit()


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    help_text = '\nThis is a Redmine Bot. Type "/registration" to make registration, \
                or "/func" to see all possible commands\n'
    bot.send_message(message.chat.id, "Hi, " + message.chat.first_name + " " +
                 message.chat.last_name + help_text)


@bot.message_handler(commands=['registration'])
def send_registration(message):
    bot.send_message(message.chat.id, "Registration started.")
    db_curs.execute("DELETE FROM users WHERE telegram_id = :1;", (message.chat.id,))
    db_conn.commit()
    bot.send_message(message.chat.id, "Enter your login: ")
    bot.register_next_step_handler(message, process_login_step)


def process_login_step(message):
    pattern_cred.set_login(message.text)
    bot.send_message(message.chat.id, "Enter your password: ")
    bot.register_next_step_handler(message, process_password_step)


def process_password_step(message):
    pattern_cred.set_password(message.text)
    bot.send_message(message.chat.id, "Registration ended.")

    try:
        usr = RM.User(username = pattern_cred.get_login(), password = pattern_cred.get_password())
        usr.set_key(usr.get_api_key(ADDRESS))
        if not usr.is_valid_user(ADDRESS):
            bot.send_message(message.chat.id, "Incorrect credentials")
            return
    except general_except.main_error as err:
        bot.send_message(message.chat.id, "Registration failed, check credentials")
        return
    db_curs.execute("INSERT INTO users (telegram_id, username, password) VALUES(:1, :2, :3);",
                    (message.chat.id, pattern_cred.get_login(), pattern_cred.get_password()))
    db_conn.commit()
    pattern_cred.clean()
    bot.send_message(message.chat.id, "Correct, well done.")


# get all projects
@bot.message_handler(commands=['all_prjs'])
def send_all_projects(message):
    redm = RM.RedmineProject(ADDRESS)
    bot.send_message(message.chat.id, "Asking for all projects:")
    projects = []
    try:
        print("try")
        projects = redm.get_all_projects()
        #print("get " + projects.__len__())
    except general_except.main_error as err:
        print("except")
        bot.send_message(message.chat.id, "Error occured")
        bot.send_message(message.chat.id, err)
        logger.warning(err.to_log)
        return
    for pjs in projects:
        bot.send_message(message.chat.id, pjs)
    return


# get only user pjs
@bot.message_handler(commands=['my_prjs'])
def send_your_projects(message):
    bot.send_message(message.chat.id, "Asking for your projects:")
    db_curs.execute("SELECT * FROM users WHERE telegram_id = :1;", (message.chat.id,))
    result = db_curs.fetchall()
    if not result:
        result = [("", "", "")]
    user = RM.User(api_key=None, username=result[0][1], password=result[0][2])
    print(db_curs.fetchall())
    redm = RM.RedmineProject(ADDRESS)
    projects = []
    try:
        projects = redm.get_only_any_user_projects(user)
    except general_except.main_error as err:
        bot.send_message(message.chat.id, "Error occured")
        bot.send_message(message.chat.id, err)
        logger.warning(err.to_log)
        return
    for pjs in projects:
        bot.send_message(message.chat.id, pjs)
    return


# get project params
@bot.message_handler(commands=['prj_params'])
def send_pj_params(message):
    bot.send_message(message.chat.id, "Enter project id: ")
    bot.register_next_step_handler(message, process_get_pj_params)


def process_get_pj_params(message):
    redm = RM.RedmineProject(ADDRESS)
    project_id = str(message.text)
    try:
        params = redm.get_project_params_by_project_id(project_id)
    except general_except.main_error as err:
        bot.send_message(message.chat.id, "Error occured")
        bot.send_message(message.chat.id, err)
        logger.warning(err.to_log)
        return
    for prm in params:
        bot.send_message(message.chat.id, prm)
    return



# create new project
@bot.message_handler(commands=['create_project'])
def create_project(message):
    bot.send_message(message.chat.id, "Enter new project name: ")
    bot.register_next_step_handler(message, process_get_pj_name)


def process_get_pj_name(message):
    pattern_project.set_name(str(message.text))
    bot.send_message(message.chat.id, "Enter new project identificator (use only small eng "
                                      "letters): ")
    bot.register_next_step_handler(message, process_get_pj_identificator)


def process_get_pj_identificator(message):
    pattern_project.set_identifier(str(message.text))
    bot.send_message(message.chat.id, "Enter new project description: ")
    bot.register_next_step_handler(message, process_get_pj_description)


def process_get_pj_description(message):
    pattern_project.set_description(str(message.text))
    bot.send_message(message.chat.id, "Enter 1 if project will be public, else 0: ")
    bot.register_next_step_handler(message, process_get_pj_ispublic)

def process_get_pj_ispublic(message):
    is_public = str(message.text)
    if is_public != '0' and is_public != '1':
        bot.send_message(message.chat.id, "Incorrect is_public parameter")
        return
    pattern_project.set_ispublic(is_public)
    print(*pattern_project.get_params())

    redm = RM.RedmineProject(ADDRESS)
    db_curs.execute("SELECT * FROM users WHERE telegram_id = :1;", (message.chat.id,))
    result = db_curs.fetchall()
    if not result:
        result = [("", "", "")]
    user = RM.User(api_key=None, username=result[0][1], password=result[0][2])

    try:
        redm.create_new_project(user, name=pattern_project.name,
                                identifier=pattern_project.identifier,
                                description=pattern_project.description,
                                is_public=pattern_project.is_public)
    except general_except.main_error as err:
        bot.send_message(message.chat.id, "Error occured")
        bot.send_message(message.chat.id, err.user_txt)
        logger.warning(err.to_log)
        return
    bot.send_message(message.chat.id, "Project created")
    return


def check_on_correct(word, checking_str):
    if len(word) == 1:
        for letter in word:
            if letter not in checking_str:
                return False
    else:
        return False
    return True



# create new issue
@bot.message_handler(commands=['create_issue'])
def create_issue(message):
    bot.send_message(message.chat.id, "Enter project id for issue: ")
    bot.register_next_step_handler(message, process_get_iss_id)


def process_get_iss_id(message):
    pattern_iss.set_project_id(str(message.text))
    bot.send_message(message.chat.id, "Enter new issue subject")
    bot.register_next_step_handler(message, process_get_iss_subject)


def process_get_iss_subject(message):
    pattern_iss.set_subject(str(message.text))
    bot.send_message(message.chat.id, "Enter issue description: ")
    bot.register_next_step_handler(message, process_get_iss_description)


def process_get_iss_description(message):
    pattern_iss.set_description(str(message.text))
    bot.send_message(message.chat.id, "Enter iss_tracker id:\n\t 1 - Bug\n\t 2 - Feature \n\t 3 - Support")
    bot.register_next_step_handler(message, process_get_iss_tracker_id)


def process_get_iss_tracker_id(message):
    tracker_id = str(message.text)
    if not check_on_correct(tracker_id, "123"):
        bot.send_message(message.chat.id, "Incorrect tracker id")
        return

    pattern_iss.set_tracker_id(int(tracker_id))
    bot.send_message(message.chat.id, "Enter status id:\n\t 1 - New\n\t 2 - In Progress\n\t" +
                    " 3 - Resolved\n\t 4 - FeedBack\n\t 5 - Closed\n\t 6 - Rejected")
    bot.register_next_step_handler(message, process_get_iss_status_id)


def process_get_iss_status_id(message):
    status_id = str(message.text)
    if not check_on_correct(status_id, "123456"):
        bot.send_message(message.chat.id, "Incorrect status id")
        return
    pattern_iss.set_status_id(int(status_id))
    bot.send_message(message.chat.id, "Enter priority id:\n\t 1 - Low\n\t 2 - Normal\n\t 3 - "
                                      "High\n\t "
                                      "4 - "
                                      "Urgent\n\t 5 "
                                      "- Immidiate")
    bot.register_next_step_handler(message, process_get_iss_priority_id)


def process_get_iss_priority_id(message):
    priority_id = str(message.text)
    if not check_on_correct(priority_id, "12345"):
        bot.send_message(message.chat.id, "Incorrect priority id")
        return
    pattern_iss.set_priority_id(int(priority_id))

    db_curs.execute("SELECT * FROM users WHERE telegram_id = :1;", (message.chat.id,))
    result = db_curs.fetchall()
    if not result:
        result = [("", "", "")]
    user = RM.User(api_key=None, username=result[0][1], password=result[0][2])

    iss = RM.Issue(url=ADDRESS, user=user)
    try:
        iss.create_new_issue(user, project_id=pattern_iss.project_id,
                                description=pattern_iss.description,
                                subject=pattern_iss.subject,
                                tracker_id=pattern_iss.tracker_id,
                                status_id=pattern_iss.status_id,
                                priority_id=pattern_iss.priority_id)
    except general_except.main_error as err:
        bot.send_message(message.chat.id, "Error occured")
        bot.send_message(message.chat.id, err.user_txt)
        logger.warning(err.to_log)
        return
    bot.send_message(message.chat.id, "Issue created")
    return


# get issue from project
@bot.message_handler(commands=['prj_issue'])
def send_issue_in_project(message):
    bot.send_message(message.chat.id, "Enter project id: ")
    bot.register_next_step_handler(message, process_get_issue_from_project)


def process_get_issue_from_project(message):
    db_curs.execute("SELECT * FROM users WHERE telegram_id = :1;", (message.chat.id,))
    result = db_curs.fetchall()
    if not result:
        result = [("", "", "")]
    user = RM.User(api_key=None, username=result[0][1], password=result[0][2])
    iss = RM.Issue(url=ADDRESS, user=user)
    project_id = str(message.text)
    try:
        answer = iss.get_all_issue_from_any_project(project_id)
    except general_except.main_error as err:
        bot.send_message(message.chat.id, "Error occured")
        bot.send_message(message.chat.id, err)
        logger.warning(err.to_log)
        return
    for ans in answer:
        bot.send_message(message.chat.id, ans)
    return

# get all issues
@bot.message_handler(commands=['all_issue'])
def send_all_issue(message):
    db_string = str(message.chat.id)
    db_curs.execute("SELECT * FROM users WHERE telegram_id = :1;", (message.chat.id,))
    result = db_curs.fetchall()
    if not result:
        result = [("", "", "")]
    user = RM.User(api_key=None, username=result[0][1], password=result[0][2])
    iss = RM.Issue(url=ADDRESS, user=user)
    try:
        list_iss = iss.get_all_issue()
    except general_except.main_error as err:
        bot.send_message(message.chat.id, "Error occured")
        bot.send_message(message.chat.id, err)
        logger.warning(err.to_log)
        return
    for e_iss in list_iss:
        bot.send_message(message.chat.id, e_iss)
    return


# change issue priority
@bot.message_handler(commands=['chg_issue_priority'])
def send_change_priority(message):
    bot.send_message(message.chat.id, "Enter issue id and new priority by a split: ")
    bot.register_next_step_handler(message, process_set_new_priority)


def process_set_new_priority(message):
    db_string = str(message.chat.id)
    db_curs.execute("SELECT * FROM users WHERE telegram_id = :1;", (message.chat.id,))
    result = db_curs.fetchall()
    if not result:
        result = [("", "", "")]
    user = RM.User(api_key=None, username=result[0][1], password=result[0][2])
    iss = RM.Issue(url=ADDRESS, user=user)
    issue_id, new_priority = str(message.text).split()
    try:
        iss.change_issue_priority(issue_id, new_priority)
    except general_except.main_error as err:
        bot.send_message(message.chat.id, "Error occured")
        bot.send_message(message.chat.id, err)
        logger.warning(err.to_log)
        return
    bot.send_message(message.chat.id, "Priority changed")
    return


# change issue status
@bot.message_handler(commands=['chg_issue_status'])
def send_change_status(message):
    bot.send_message(message.chat.id, "Enter issue id and new status a split: ")
    bot.send_message(message.chat.id, "# statud_id:\n 1 - New,\n 2 - In Progress,\n 3 - Resolved," +
        " 4 - FeedBack,\n 5 - Closed,\n 6 - FeedBack.")
    bot.register_next_step_handler(message, process_set_new_status)


def process_set_new_status(message):
    db_curs.execute("SELECT * FROM users WHERE telegram_id = :1;", (message.chat.id,))
    result = db_curs.fetchall()
    if not result:
        result = [("", "", "")]
    user = RM.User(api_key=None, username=result[0][1], password=result[0][2])
    iss = RM.Issue(url=ADDRESS, user=user)
    issue_id, new_status = str(message.text).split()
    try:
        iss.change_issue_status(issue_id, new_status)
    except general_except.main_error as err:
        bot.send_message(message.chat.id, "Error occured")
        bot.send_message(message.chat.id, err)
        logger.warning(err.to_log)
        return
    bot.send_message(message.chat.id, "Status changed")
    return


# delete issue
@bot.message_handler(commands=['del_issue'])
def send_delete_issue(message):
    bot.send_message(message.chat.id, "Enter issue id: ")
    bot.register_next_step_handler(message, process_get_id_for_delete)


def process_get_id_for_delete(message):
    db_curs.execute("SELECT * FROM users WHERE telegram_id = :1", (message.chat.id,))
    result = db_curs.fetchall()
    if not result:
        result = [("", "", "")]
    user = RM.User(api_key=None, username=result[0][1], password=result[0][2])
    iss = RM.Issue(url=ADDRESS, user=user)
    issue_id = str(message.text)
    result = False
    try:
        result = iss.delete_issue(issue_id)
    except general_except.main_error as err:
        bot.send_message(message.chat.id, "Error occured")
        bot.send_message(message.chat.id, err)
        logger.warning(err.to_log)
        return
    if result:
        bot.send_message(message.chat.id, "Issue deleted")
    else:
        bot.send_message(message.chat.id, "Deleting failed")
    return


# delete project
@bot.message_handler(commands=['del_prj'])
def send_delete_project(message):
    bot.send_message(message.chat.id, "Enter project id: ")
    bot.register_next_step_handler(message, process_get_prj_id_for_delete)


def process_get_prj_id_for_delete(message):
    db_curs.execute("SELECT * FROM users WHERE telegram_id = :1;", (message.chat.id,))
    result = db_curs.fetchall()
    if not result:
        result = [("", "", "")]
    user = RM.User(api_key=None, username=result[0][1], password=result[0][2])
    print(db_curs.fetchall())
    redm = RM.RedmineProject(ADDRESS)
    prj_id = str(message.text)
    result = False
    try:
        result = redm.delete_project(user, prj_id)
    except general_except.main_error as err:
        bot.send_message(message.chat.id, "Error occured")
        bot.send_message(message.chat.id, err)
        logger.warning(err.to_log) # to log
        return
    if result:
        bot.send_message(message.chat.id, "Project deleted")
    else:
        bot.send_message(message.chat.id, "Deleting failed")
    return


# help or start
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Hi, " + message.chat.first_name + " " +
        message.chat.last_name + 'type /func to see all posible functions')


print("Start polling")
bot.send_message(169487942, "Wake up neo, we starting")
bot.polling()
print("Stop polling")
