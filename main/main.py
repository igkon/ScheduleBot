import telebot
import requests

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
                if dates != None and len(dates) > 0:
                    for date in dates:
                        res = requests.get(cfg['server_url'] + '/schedule/' + str(date),
                                           auth=(users_login[message.chat.id], users_password[message.chat.id]))
                        if not res.json():
                            tb.send_message(message.chat.id, 'На дату ' + date.strftime('%d.%m.%Y') + ' нет задач')
                        else:
                            tb.send_message(message.chat.id, 'Расписание на ' + date.strftime('%d.%m.%Y'))
                            for i, subj in enumerate(res.json()):
                                tb.send_message(message.chat.id, str(i+1) + '. ' + subj['subject']['title'])
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
            # tasks endpoint example site.ru/tasks
            dates = parse_command_date(tb, message)
            try:
                if dates != None and len(dates) > 0:
                    res = requests.get(cfg['server_url'] + '/tasks', auth=(users_login[message.chat.id],
                                                                           users_password[message.chat.id]))
                    if not res.json():
                        tb.send_message(message.chat.id, 'У вас нет проставленных задач')
                    else:
                        tasks_for_dates = list()
                        for date in dates:
                            for task in res.json():
                                if task['due_date'] == str(date):
                                    tasks_for_dates.append(task)
                        if len(tasks_for_dates) == 0:
                            tb.send_message(message.chat.id, 'Нет задач на указанную(ые) дату(ы)')
                        else:
                            sorted_tasks = sorted(tasks_for_dates, key=lambda k: k['due_date'])
                            for i, task in enumerate(sorted_tasks):
                                tb.send_message(message.chat.id, str(i+1) + '. ' + task['title'] + ' ' +
                                                task['due_date'])
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
                response = requests.get(cfg['server_url'] + '/tasks', auth=(users_login[message.chat.id],
                                                                            users_password[message.chat.id]))
                if response.status_code == 200:
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
                users_current_state[message.chat.id] = States.LOGIN_ENTERING
        elif users_current_state[message.chat.id] == States.AUTHORIZED:
            command = message.text.split()[0]
            if command != '/schedule' and command != '/tasks' and command != '/help':
                tb.send_message(message.chat.id, 'Неверно введенная команда')


if __name__ == '__main__':
    tb.polling()
