# -*- coding: utf-8 -*-
import telebot
import get_key
import data_base
import credent

DB = data_base.UserDataBase()
cred = credent.Credent()
bot = telebot.TeleBot(str(get_key.get()))

def parser(text):
    return "text", 0


@bot.message_handler(commands=['func'])
def send_func(message):
    bot.reply_to(message, "List of possible commands:")
    text = '/start or /help - welcome message\n\
            /registration - reg process\n\
            /func - list of possible functions\n\
            /get_all_news - get all new news\n\
            /get_news - get news by id'
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    help_text = '\nThis is a Redmine Bot. Type "/registration" to make registration, \
                or "/func" to see all possible commands\n'
    bot.reply_to(message, "Hi, " + message.chat.first_name + " " +
                 message.chat.last_name + help_text)


@bot.message_handler(commands=['registration'])
def send_registration(message):
    bot.reply_to(message, "Registration started.")
    bot.send_message(message.chat.id, "Enter your login: ")
    bot.register_next_step_handler(message, process_login_step)


def process_login_step(message):
    cred.setLogin(message.text)
    bot.send_message(message.chat.id, "Enter your password: ")
    bot.register_next_step_handler(message, process_password_step)


def process_password_step(message):
    cred.setPassword(message.text)
    bot.send_message(message.chat.id, "Registration ended.")
    DB.create_user(message.chat.id, message.chat.first_name + " " +
                   message.chat.last_name, cred.get())
    bot.send_message(message.chat.id, "Checking credentials.\n")
    result = DB.check_user_credentials(message.chat.id)
    if result:
        bot.send_message(message.chat.id, "Correct, well done.")
    else:
        DB.delete_user(message.user.id)
        bot.send_message(message.chat.id, "Incorrect combination, " +
                         "profile deleted, try again.")


def find_news(user):
    return "there's no happy in this town", 0


def get_news(user_id):
    user = DB.get_user_credentials(user_id)
    if user == 'None':
        return "Error occured, try make registration again"
    news, error = find_news(user)
    if error:
        return "Error occured, try again"
    return news


@bot.message_handler(commands=['get_all_news'])
def send_get_news(message):
    bot.reply_to(message, "Asking for news:")
    news = get_news(message.chat.id)
    bot.send_message(message.chat.id, news)


def find_news_by_id(user, news_id):
    return "newwws", 0


def get_news_by_id(user_id, news_id):
    user = DB.get_user_credentials(user_id)
    if user == 'None':
        return "Error occured, try make registration again"
    news, error = find_news_by_id(user, news_id)
    if error:
        return "News ID is incorrect"
    return news


@bot.message_handler(commands=['get_news'])
def send_get_news_by_id(message):
    bot.send_message(message.chat.id, "Enter news id: ")
    bot.register_next_step_handler(message, process_get_news_by_id)


def process_get_news_by_id(message):
    news_id = str(message.text)
    bot.reply_to(message, "Asking for news with id '" + news_id + "'")
    news = get_news_by_id(message.chat.id, news_id)
    bot.send_message(message.chat.id, news)


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, "Hi, " + message.chat.first_name + " " +
                 message.chat.last_name + 'type /func to see all posible functions')

'''
@bot.message_handler(content_types=['text'])
def send_welcome(message):
    msg = bot.send_message(message.chat.id, "Hi, " + message.chat.first_name + " " + message.chat.last_name + ', please, use something from:\n/start\n/help\n/func')
'''

print("Start polling")
bot.send_message(169487942, "Wake up neo, we starting")
# bot.send_message(248180981, "Hello, muchacho, bot started")
bot.polling()
print("Stop polling")
