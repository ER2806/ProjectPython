CONFIG = "config"

def get_telegram_key():
    with open(CONFIG) as config_file:
        for row in config_file:
            if "TelegramKey" in row:
                return list(map(str, row.split()))[1]

def get_address():
    with open(CONFIG) as config_file:
        for row in config_file:
            if "Address" in row:
                return list(map(str, row.split()))[1]

def get_log():
    with open(CONFIG) as config_file:
        for row in config_file:
            if "Log" in row:
                return list(map(str, row.split()))[1]


