import telebot

from util.state import States

from bot_config import config as cfg


tb = telebot.TeleBot(cfg['token'])

current_state = States.INITIAL

user_login = ''


@tb.message_handler(commands=['start'])
def start_message(message):
    global current_state
    tb.send_message(message.chat.id,
                              'Добро пожаловать в приложение-расписание! \n'
                              'Здесь вы можете просматривать свое расписание и список задач. \n'
                              'Для продолжения работы необходимо авторизоваться.')
    tb.send_message(message.chat.id, 'Введите ваш логин')
    current_state = States.LOGIN_ENTERING


@tb.message_handler(content_types=['text'])
def schedule_bot_finite_automate(message):
    global current_state
    global user_login
    if current_state == States.LOGIN_ENTERING:
        user_login = message.text
        tb.send_message(message.chat.id, 'Введите ваш пароль')
        current_state = States.PASSWORD_ENTERING
    elif current_state == States.PASSWORD_ENTERING:
        pass
    elif current_state == States.AUTHORIZED:
        pass


if __name__ == '__main__':
    tb.polling()
