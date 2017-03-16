import telepot
import GETKEY

rf = open("key", "r");
token = GETKEY.get()
#print(token == '334638429:AAGFfw_ZJo8tN5nJBjAov8woxRkiFnqCnA0')
TelegramBot = telepot.Bot(token);
print(TelegramBot.getMe())

