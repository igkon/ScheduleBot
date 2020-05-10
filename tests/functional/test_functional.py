import pytest

import io
import sys

import main.cmd
from main.bot_config import config as cfg

import util.mocks
import util.state as st
import util.date_functions

# Test vars
main.cmd.tb = util.mocks.TelebotMock()
user_id = 1
login = 'alex'
password = 'qwe1'


@pytest.fixture(autouse=True)
def run_around_tests():

    yield

    main.cmd.users_current_state.clear()
    main.cmd.users_login.clear()
    main.cmd.users_password.clear()


# FR_Id_28 FR_Id_29 FR_Id_30 FR_Id_32 FR_Id_33
def test_success_login():
    captured_output = io.StringIO()
    sys.stdout = captured_output

    msg = util.mocks.MessageMock('/start', user_id)

    main.cmd.start_message(msg)
    assert captured_output.getvalue().__contains__(cfg['start_message'])
    assert main.cmd.users_current_state[user_id] == st.States.LOGIN_ENTERING

    msg.text = login
    main.cmd.authorization_finite_automate(msg)
    assert main.cmd.users_current_state[user_id] == st.States.PASSWORD_ENTERING

    msg.text = password
    main.cmd.authorization_finite_automate(msg)
    assert main.cmd.users_current_state[user_id] == st.States.AUTHORIZED
    assert captured_output.getvalue().__contains__('Вы успешно авторизовались')
    assert captured_output.getvalue().__contains__('Узнать список доступных команд можно при помощи /help')


# FR_Id_34
def test_help_command():
    captured_output = io.StringIO()
    sys.stdout = captured_output

    msg = util.mocks.MessageMock('/help', user_id)
    main.cmd.users_current_state[user_id] = st.States.AUTHORIZED

    main.cmd.help_command(msg)
    assert captured_output.getvalue().__contains__(cfg['help_message'])


# FR_Id_35 FR_Id_36
def test_schedule_command():
    captured_output = io.StringIO()
    sys.stdout = captured_output

    msg = util.mocks.MessageMock('/start', user_id)

    main.cmd.start_message(msg)

    msg.text = login
    main.cmd.authorization_finite_automate(msg)

    msg.text = password
    main.cmd.authorization_finite_automate(msg)

    msg.text = '/schedule 11.05.2020'
    main.cmd.schedule_getting_command(msg)
    assert captured_output.getvalue().__contains__('1. Math')

    msg.text = '/schedule 10.05.2020'
    main.cmd.schedule_getting_command(msg)
    assert captured_output.getvalue().__contains__('На дату 10.05.2020 нет задач')


# FR_Id_35 FR_Id_37
def test_schedule_command_range():
    captured_output = io.StringIO()
    sys.stdout = captured_output

    msg = util.mocks.MessageMock('/start', user_id)

    main.cmd.start_message(msg)

    msg.text = login
    main.cmd.authorization_finite_automate(msg)

    msg.text = password
    main.cmd.authorization_finite_automate(msg)

    msg.text = '/schedule 11.05.2020-13.05.2020'
    main.cmd.schedule_getting_command(msg)
    assert captured_output.getvalue().__contains__('Расписание на 11.05.2020')
    assert captured_output.getvalue().__contains__('1. Math')

    assert captured_output.getvalue().__contains__('Расписание на 12.05.2020')
    assert captured_output.getvalue().__contains__('1. Math')

    assert captured_output.getvalue().__contains__('Расписание на 13.05.2020')
    assert captured_output.getvalue().__contains__('1. Math')

    msg.text = '/schedule 10.05.2020-11.05.2020'
    main.cmd.schedule_getting_command(msg)
    assert captured_output.getvalue().__contains__('На дату 10.05.2020 нет задач')
    assert captured_output.getvalue().__contains__('Расписание на 11.05.2020')
    assert captured_output.getvalue().__contains__('1. Math')


# FR_Id_35 FR_Id_38
def test_tasks_command():
    captured_output = io.StringIO()
    sys.stdout = captured_output

    msg = util.mocks.MessageMock('/start', user_id)

    main.cmd.start_message(msg)

    msg.text = login
    main.cmd.authorization_finite_automate(msg)

    msg.text = password
    main.cmd.authorization_finite_automate(msg)

    msg.text = '/tasks 11.05.2020'
    main.cmd.tasks_getting_command(msg)
    assert captured_output.getvalue().__contains__('1. Learn theorem 2020-05-11')


# FR_Id_35 FR_Id_39
def test_tasks_command_range():
    captured_output = io.StringIO()
    sys.stdout = captured_output

    msg = util.mocks.MessageMock('/start', user_id)

    main.cmd.start_message(msg)

    msg.text = login
    main.cmd.authorization_finite_automate(msg)

    msg.text = password
    main.cmd.authorization_finite_automate(msg)

    msg.text = '/tasks 11.05.2020-13.05.2020'
    main.cmd.tasks_getting_command(msg)
    assert captured_output.getvalue().__contains__('1. Learn theorem 2020-05-11')
    assert captured_output.getvalue().__contains__('2. Draw the graph 2020-05-12')


# FR_Id_31
def test_failed_login():
    captured_output = io.StringIO()
    sys.stdout = captured_output

    msg = util.mocks.MessageMock('/start', user_id)

    main.cmd.start_message(msg)
    assert captured_output.getvalue().__contains__(cfg['start_message'])
    assert main.cmd.users_current_state[user_id] == st.States.LOGIN_ENTERING

    msg.text = login
    main.cmd.authorization_finite_automate(msg)
    assert main.cmd.users_current_state[user_id] == st.States.PASSWORD_ENTERING

    msg.text = 'incorrect_password'
    main.cmd.authorization_finite_automate(msg)
    assert captured_output.getvalue().__contains__('Неверный логин или пароль. Попробуйте снова')
    assert main.cmd.users_current_state[user_id] == st.States.LOGIN_ENTERING
