import telebot
import requests
import datetime

from util.state import States
from util.date_functions import convert_date_list_to_date_object

from bot_config import config as cfg


tb = telebot.TeleBot(cfg['token'])

current_state = States.INITIAL

user_login = ''
# ETO ZHEST
user_password = ''

@tb.message_handler(commands=['start'])
def start_message(message):
    global current_state
    tb.send_message(message.chat.id, cfg['start_message'])
    tb.send_message(message.chat.id, 'Введите ваш логин')
    current_state = States.LOGIN_ENTERING


@tb.message_handler(commands=['schedule'])
def schedule_getting_command(message):
    if current_state == States.AUTHORIZED:
        # schedule endpoint example site.ru/schedule/2020-01-19
        try:
            date = message.text.split()[1]
            if '-' in date:
                date_range = date.split('-')
                print(date_range)
                if len(date_range) != 2:
                    raise IndexError
                date_list_left = date_range[0].split('.')
                print(date_list_left)
                date_object_left = convert_date_list_to_date_object(date_list_left)
                print(date_object_left)
                date_list_right = date_range[1].split('.')
                print(date_list_right)
                date_object_right = convert_date_list_to_date_object(date_list_right)
                date_delta = date_object_right - date_object_left
                # нашли разницу в днях между двумя датами
                if date_delta.days < 0 or date_delta.days > 7:
                    tb.send_message(message.chat.id, 'Неподдерживаемый промежуток между датами. Число дней > 7 или < 0')
                    return
                else:
                    for i in range(0, date_delta.days + 1):
                        # цикл по всем датам в этом интервале. Для каждой даты делаем запрос и печатаем.
                        date_diff = datetime.timedelta(days=i)
                        date_cycle = date_object_left + date_diff
                        # здесь нужно знать, что прийдет в response, чтобы красиво распечатать
                        try:
                            res = requests.get(cfg['server_url']+'/schedule/'+str(date_cycle),
                                               auth=(user_login, user_password))
                            print(res)
                        except ValueError:
                            tb.send_message(message.chat.id, 'Потеряно соединение с сервером. Попробуйте снова')
                            break
            else:
                date_list = date.split('.')
                date_object = convert_date_list_to_date_object(date_list)
                try:
                    res = requests.get(cfg['server_url']+'/schedule/'+str(date_object), auth=(user_login, user_password))
                    # здесь нужно знать, что прийдет в response, чтобы красиво распечатать
                    print(res)
                except ValueError:
                    tb.send_message(message.chat.id, 'Потеряно соединение с сервером. Попробуйте снова')
        except IndexError:
            tb.send_message(message.chat.id, 'Введите дату/даты корректно. Для подробной информации используйте /help')
        except ValueError:
            tb.send_message(message.chat.id, 'Введите дату/даты корректно. Для подробной информации используйте /help')
        except Exception:
            tb.send_message(message.chat.id, 'Потеряно соединение с сервером. Попробуйте снова')


# Пока дублирование кода, потом зарефакторю (или нет)
@tb.message_handler(commands=['tasks'])
def tasks_getting_command(message):
    if current_state == States.AUTHORIZED:
        # tasks endpoint example site.ru/tasks/2020-01-19
        try:
            date = message.text.split()[1]
            if '-' in date:
                date_range = date.split('-')
                print(date_range)
                if len(date_range) != 2:
                    raise IndexError
                date_list_left = date_range[0].split('.')
                print(date_list_left)
                date_object_left = convert_date_list_to_date_object(date_list_left)
                print(date_object_left)
                date_list_right = date_range[1].split('.')
                print(date_list_right)
                date_object_right = convert_date_list_to_date_object(date_list_right)
                date_delta = date_object_right - date_object_left
                # нашли разницу в днях между двумя датами
                if date_delta.days < 0 or date_delta.days > 7:
                    tb.send_message(message.chat.id, 'Неподдерживаемый промежуток между датами. Число дней > 7 или < 0')
                    return
                else:
                    for i in range(0, date_delta.days + 1):
                        # цикл по всем датам в этом интервале. Для каждой даты делаем запрос и печатаем.
                        date_diff = datetime.timedelta(days=i)
                        date_cycle = date_object_left + date_diff
                        # здесь нужно знать, что прийдет в response, чтобы красиво распечатать
                        try:
                            res = requests.get(cfg['server_url']+'/schedule/'+str(date_cycle),
                                               auth=(user_login, user_password))
                            print(res)
                        except ValueError:
                            tb.send_message(message.chat.id, 'Потеряно соединение с сервером. Попробуйте снова')
                            break
            else:
                date_list = date.split('.')
                date_object = convert_date_list_to_date_object(date_list)
                try:
                    res = requests.get(cfg['server_url']+'/schedule/'+str(date_object), auth=(user_login, user_password))
                    # здесь нужно знать, что прийдет в response, чтобы красиво распечатать
                    print(res)
                except ValueError:
                    tb.send_message(message.chat.id, 'Потеряно соединение с сервером. Попробуйте снова')
        except IndexError:
            tb.send_message(message.chat.id, 'Введите дату/даты корректно. Для подробной информации используйте /help')
        except ValueError:
            tb.send_message(message.chat.id, 'Введите дату/даты корректно. Для подробной информации используйте /help')
        except Exception:
            tb.send_message(message.chat.id, 'Потеряно соединение с сервером. Попробуйте снова')


@tb.message_handler(commands=['help'])
def help_command(message):
    if current_state == States.AUTHORIZED:
        tb.send_message(message.chat.id, cfg['help_message'])


@tb.message_handler(content_types=['text'])
def authorization_finite_automate(message):
    global current_state
    global user_login
    global user_password
    if current_state == States.LOGIN_ENTERING:
        user_login = message.text
        tb.send_message(message.chat.id, 'Введите ваш пароль')
        current_state = States.PASSWORD_ENTERING
    elif current_state == States.PASSWORD_ENTERING:
        user_password = message.text
        try:
            response = requests.get(cfg['server_url']+'/users', auth=(user_login, user_password))
            # mock checking of authorization (я не знаю как это должно выглядеть и что будет в response)
            if response.json().authorized:
                tb.send_message(message.chat.id, 'Вы успешно авторизовались')
                tb.send_message(message.chat.id, 'Узнать список доступных команд можно при помощи /help')
                current_state = States.AUTHORIZED
            else:
                tb.send_message(message.chat.id, 'Неверный логин или пароль. Попробуйте снова')
                tb.send_message(message.chat.id, 'Введите ваш логин')
                current_state = States.LOGIN_ENTERING
        except Exception:
            tb.send_message(message.chat.id, 'Потеряно соединение с сервером. Попробуйте снова')
            tb.send_message(message.chat.id, 'Введите ваш логин')
            current_state = States.LOGIN_ENTERING
            # for debug current_state = States.AUTHORIZED
    elif current_state == States.AUTHORIZED:
        command = message.text.split()[0]
        if command != '/schedule' and command != '/tasks' and command != '/help':
            tb.send_message(message.chat.id, 'Неверно введенная команда')


if __name__ == '__main__':
    tb.polling()
