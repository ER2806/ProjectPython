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
"""
db_curs.execute('''CREATE TABLE users
                (telegram_id INTEGER PRIMARY KEY, username VARCHAR(100),
                password VARCHAR(100))
                ''')

db_conn.commit()
"""


cred = credent.Credent()
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


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    help_text = '\nThis is a Redmine Bot. Type "/registration" to make registration, \
                or "/func" to see all possible commands\n'
    bot.send_message(message.chat.id, "Hi, " + message.chat.first_name + " " +
                 message.chat.last_name + help_text)


@bot.message_handler(commands=['registration'])
def send_registration(message):
    bot.send_message(message.chat.id, "Registration started.")
    db_string = str(message.chat.id)
    db_curs.execute("DELETE FROM users WHERE telegram_id=" + db_string + ";")
    db_conn.commit()
    bot.send_message(message.chat.id, "Enter your login: ")
    bot.register_next_step_handler(message, process_login_step)


def process_login_step(message):
    cred.set_login(message.text)
    bot.send_message(message.chat.id, "Enter your password: ")
    bot.register_next_step_handler(message, process_password_step)


def process_password_step(message):
    cred.set_password(message.text)
    bot.send_message(message.chat.id, "Registration ended.")
    db_string = str(message.chat.id) + ",'" + cred.get_login() + "', '" + cred.get_password() + "'"
    db_curs.execute("INSERT INTO users (telegram_id, username, password) VALUES(" + db_string +
                    ");")
    db_conn.commit()
    cred.clean()
    bot.send_message(message.chat.id, "Correct, well done.")


# get all projects
@bot.message_handler(commands=['all_prjs'])
def send_all_projects(message):
    redm = RM.RedmineProject(ADDRESS)
    bot.send_message(message.chat.id, "Asking for all projects:")
    try:
        projects = redm.get_all_projects()
    except general_except.main_error as err:
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
    db_string = str(message.chat.id)
    db_curs.execute("SELECT * FROM users WHERE telegram_id=" + db_string + ";")
    result = db_curs.fetchall()
    if not result:
        result = [("", "", "")]
    user = RM.User(api_key=None, username=result[0][1], password=result[0][2])
    print(db_curs.fetchall())
    redm = RM.RedmineProject(ADDRESS)
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


# get issue from project
@bot.message_handler(commands=['prj_issue'])
def send_issue_in_project(message):
    bot.send_message(message.chat.id, "Enter project id: ")
    bot.register_next_step_handler(message, process_get_issue_from_project)


def process_get_issue_from_project(message):
    db_string = str(message.chat.id)
    db_curs.execute("SELECT * FROM users WHERE telegram_id=" + db_string + ";")
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
    db_curs.execute("SELECT * FROM users WHERE telegram_id=" + db_string + ";")
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
    db_curs.execute("SELECT * FROM users WHERE telegram_id=" + db_string + ";")
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
    db_string = str(message.chat.id)
    db_curs.execute("SELECT * FROM users WHERE telegram_id=" + db_string + ";")
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
    db_string = str(message.chat.id)
    db_curs.execute("SELECT * FROM users WHERE telegram_id=" + db_string + ";")
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
    db_string = str(message.chat.id)
    db_curs.execute("SELECT * FROM users WHERE telegram_id=" + db_string + ";")
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


'''
@bot.message_handler(content_types=['text'])
def send_welcome(message):
    msg = bot.send_message(message.chat.id, "Hi, " + message.chat.first_name + " " + message.chat.last_name + ', please, use something from:\n/start\n/help\n/func')
'''

print("Start polling")
bot.send_message(169487942, "Wake up neo, we starting")
bot.polling()
print("Stop polling")
