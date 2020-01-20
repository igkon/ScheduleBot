import telebot
import requests
import datetime

from util.state import States
from util.date_functions import parse_command_date

from bot_config import config as cfg


tb = telebot.TeleBot(cfg['token'])

users_current_state = {}

users_login = {}

# ETO ZHEST
users_password = {}


@tb.message_handler(commands=['start'])
def start_message(message):
    tb.send_message(message.chat.id, cfg['start_message'])
    if message.chat.id in users_current_state:
        if users_current_state[message.chat.id] == States.LOGIN_ENTERING:
            tb.send_message(message.chat.id, 'Команда не может быть логином. Попробуйте снова')
        if users_current_state[message.chat.id] == States.PASSWORD_ENTERING:
            tb.send_message(message.chat.id, 'Команда не может быть паролем. Попробуйте снова')
    else:
        tb.send_message(message.chat.id, 'Введите ваш логин')
        users_current_state[message.chat.id] = States.LOGIN_ENTERING


@tb.message_handler(commands=['schedule'])
def schedule_getting_command(message):
    if message.chat.id in users_current_state:
        if users_current_state[message.chat.id] == States.LOGIN_ENTERING:
            tb.send_message(message.chat.id, 'Команда не может быть логином. Попробуйте снова')
        if users_current_state[message.chat.id] == States.PASSWORD_ENTERING:
            tb.send_message(message.chat.id, 'Команда не может быть паролем. Попробуйте снова')
        if users_current_state[message.chat.id] == States.AUTHORIZED:
            # schedule endpoint example site.ru/schedule/2020-01-19
            dates = parse_command_date(tb, message)
            try:
                if dates != None and len(dates)>0:
                    for date in dates:
                        # здесь нужно знать, что прийдет в response, чтобы красиво распечатать
                        res = requests.get(cfg['server_url']+'/schedule/'+str(date),
                                           auth=(users_login[message.chat.id], users_password[message.chat.id]))
                        print(res)
            except ValueError:
                tb.send_message(message.chat.id, 'Потеряно соединение с сервером. Попробуйте снова')


@tb.message_handler(commands=['tasks'])
def tasks_getting_command(message):
    if message.chat.id in users_current_state:
        if users_current_state[message.chat.id] == States.LOGIN_ENTERING:
            tb.send_message(message.chat.id, 'Команда не может быть логином. Попробуйте снова')
        if users_current_state[message.chat.id] == States.PASSWORD_ENTERING:
            tb.send_message(message.chat.id, 'Команда не может быть паролем. Попробуйте снова')
        if users_current_state[message.chat.id] == States.AUTHORIZED:
            # tasks endpoint example site.ru/tasks/2020-01-19
            dates = parse_command_date(tb, message)
            try:
                if dates != None and len(dates)>0:
                    for date in dates:
                        # здесь нужно знать, что прийдет в response, чтобы красиво распечатать
                        res = requests.get(cfg['server_url']+'/tasks/'+str(date),
                                           auth=(users_login[message.chat.id], users_password[message.chat.id]))
                        print(res)
            except ValueError:
                tb.send_message(message.chat.id, 'Потеряно соединение с сервером. Попробуйте снова')


@tb.message_handler(commands=['help'])
def help_command(message):
    if message.chat.id in users_current_state:
        if users_current_state[message.chat.id] == States.LOGIN_ENTERING:
            tb.send_message(message.chat.id, 'Команда не может быть логином. Попробуйте снова')
        if users_current_state[message.chat.id] == States.PASSWORD_ENTERING:
            tb.send_message(message.chat.id, 'Команда не может быть паролем. Попробуйте снова')
        if users_current_state[message.chat.id] == States.AUTHORIZED:
            tb.send_message(message.chat.id, cfg['help_message'])


@tb.message_handler(content_types=['text'])
def authorization_finite_automate(message):
    if message.chat.id in users_current_state:
        if users_current_state[message.chat.id] == States.LOGIN_ENTERING:
            users_login[message.chat.id] = message.text
            tb.send_message(message.chat.id, 'Введите ваш пароль')
            users_current_state[message.chat.id] = States.PASSWORD_ENTERING
        elif users_current_state[message.chat.id] == States.PASSWORD_ENTERING:
            users_password[message.chat.id] = message.text
            try:
                response = requests.get(cfg['server_url']+'/users', auth=(users_login[message.chat.id],
                                                                          users_password[message.chat.id]))
                # mock checking of authorization (я не знаю как это должно выглядеть и что будет в response)
                if response.json().authorized:
                    tb.send_message(message.chat.id, 'Вы успешно авторизовались')
                    tb.send_message(message.chat.id, 'Узнать список доступных команд можно при помощи /help')
                    users_current_state[message.chat.id] = States.AUTHORIZED
                else:
                    tb.send_message(message.chat.id, 'Неверный логин или пароль. Попробуйте снова')
                    tb.send_message(message.chat.id, 'Введите ваш логин')
                    users_current_state[message.chat.id] = States.LOGIN_ENTERING
            except Exception:
                tb.send_message(message.chat.id, 'Потеряно соединение с сервером. Попробуйте снова')
                tb.send_message(message.chat.id, 'Введите ваш логин')
                # users_current_state[message.chat.id] = States.LOGIN_ENTERING
                # for debug
                users_current_state[message.chat.id] = States.AUTHORIZED
        elif users_current_state[message.chat.id] == States.AUTHORIZED:
            command = message.text.split()[0]
            if command != '/schedule' and command != '/tasks' and command != '/help':
                tb.send_message(message.chat.id, 'Неверно введенная команда')


if __name__ == '__main__':
    tb.polling()
