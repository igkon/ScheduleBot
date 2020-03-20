import pytest
import requests_mock

import io
import sys

import main.main
from main.bot_config import config as cfg

import util.mocks
import util.state as st
import util.date_functions


main.main.tb = util.mocks.TelebotMock()
user_id = 1
test_login = 'login'
test_password = 'password'

@pytest.fixture(autouse=True)
def run_around_tests():

    yield

    main.main.users_current_state.clear()
    main.main.users_login.clear()
    main.main.users_password.clear()


def test_start_message():
    captured_output = io.StringIO()
    sys.stdout = captured_output

    msg = util.mocks.MessageMock('/start', user_id)

    main.main.start_message(msg)
    assert captured_output.getvalue().__contains__(cfg['start_message'])
    captured_output.truncate(0)
    captured_output.seek(0)

    check_command_as_credentials(msg, captured_output)

    main.main.users_current_state[user_id] = st.States.AUTHORIZED
    main.main.start_message(msg)
    assert captured_output.getvalue().__contains__('Вы вышли из профиля')
    assert main.main.users_current_state[user_id] == st.States.LOGIN_ENTERING
    captured_output.truncate(0)
    captured_output.seek(0)


def test_help_command():
    captured_output = io.StringIO()
    sys.stdout = captured_output

    main.main.tb = util.mocks.TelebotMock()
    msg = util.mocks.MessageMock('/help', user_id)
    main.main.help_command(msg)
    assert len(captured_output.getvalue()) == 0
    captured_output.truncate(0)
    captured_output.seek(0)

    check_command_as_credentials(msg, captured_output)

    main.main.users_current_state[user_id] = st.States.AUTHORIZED
    main.main.help_command(msg)
    assert captured_output.getvalue().__contains__(cfg['help_message'])


def test_authorization_finite_automate():
    captured_output = io.StringIO()
    sys.stdout = captured_output

    main.main.tb = util.mocks.TelebotMock()
    msg = util.mocks.MessageMock(test_login, user_id)
    main.main.authorization_finite_automate(msg)
    assert len(captured_output.getvalue()) == 0
    captured_output.truncate(0)
    captured_output.seek(0)

    main.main.users_current_state[user_id] = st.States.LOGIN_ENTERING
    main.main.authorization_finite_automate(msg)
    assert main.main.users_current_state[user_id] == st.States.PASSWORD_ENTERING
    assert main.main.users_login[user_id] == test_login

    msg.text = test_password
    with requests_mock.mock() as m:
        m.get(cfg['server_url'] + '/tasks', text='data', status_code=200)
        main.main.authorization_finite_automate(msg)
    assert main.main.users_current_state[user_id] == st.States.AUTHORIZED
    assert main.main.users_password[user_id] == test_password

    main.main.users_current_state[user_id] = st.States.PASSWORD_ENTERING
    with requests_mock.mock() as m:
        m.get(cfg['server_url'] + '/tasks', text='data', status_code=404)
        main.main.authorization_finite_automate(msg)
    assert main.main.users_current_state[user_id] == st.States.LOGIN_ENTERING

    main.main.users_current_state[user_id] = st.States.PASSWORD_ENTERING
    with requests_mock.mock() as m:
        m.get(cfg['server_url'] + '/tasks', exc=Exception)
        main.main.authorization_finite_automate(msg)
    assert main.main.users_current_state[user_id] == st.States.LOGIN_ENTERING

    msg.text = 'random'
    main.main.users_current_state[user_id] = st.States.AUTHORIZED
    main.main.authorization_finite_automate(msg)
    assert captured_output.getvalue().__contains__('Неверно введенная команда')


def test_schedule_getting_command():
    captured_output = io.StringIO()
    sys.stdout = captured_output
    msg = util.mocks.MessageMock('/schedule 10.10.2010', user_id)
    main.main.users_login[user_id] = test_login
    main.main.users_password[user_id] = test_password

    check_command_as_credentials(msg, captured_output)

    main.main.users_current_state[user_id] = st.States.AUTHORIZED
    with requests_mock.mock() as m:
        m.get(cfg['server_url'] + '/schedule/2010-10-10', json=[])
        main.main.schedule_getting_command(msg)
    assert captured_output.getvalue().__contains__('На дату 10.10.2010 нет задач')
    captured_output.truncate(0)
    captured_output.seek(0)

    with requests_mock.mock() as m:
        m.get(cfg['server_url'] + '/schedule/2010-10-10', json=[{'subject':{'title': 'Programming'}},
                                                                {'subject':{'title': 'Math'}}])
        main.main.schedule_getting_command(msg)
    assert captured_output.getvalue().__contains__('1. Programming')
    assert captured_output.getvalue().__contains__('2. Math')
    captured_output.truncate(0)
    captured_output.seek(0)

    with requests_mock.mock() as m:
        m.get(cfg['server_url'] + '/schedule/2010-10-10', exc=ValueError)
        main.main.schedule_getting_command(msg)
    assert captured_output.getvalue().__contains__('Потеряно соединение с сервером')
    captured_output.truncate(0)
    captured_output.seek(0)


def test_tasks_getting_command():
    captured_output = io.StringIO()
    sys.stdout = captured_output
    msg = util.mocks.MessageMock('/tasks 10.10.2010', user_id)
    main.main.users_login[user_id] = test_login
    main.main.users_password[user_id] = test_password

    check_command_as_credentials(msg, captured_output)

    main.main.users_current_state[user_id] = st.States.AUTHORIZED

    with requests_mock.mock() as m:
        m.get(cfg['server_url'] + '/tasks', json=[])
        main.main.tasks_getting_command(msg)
    assert captured_output.getvalue().__contains__('У вас нет проставленных задач')
    captured_output.truncate(0)
    captured_output.seek(0)

    with requests_mock.mock() as m:
        m.get(cfg['server_url'] + '/tasks', json=[{'due_date': '2010-10-09'}, {'due_date': '2010-10-08'}])
        main.main.tasks_getting_command(msg)
    assert captured_output.getvalue().__contains__('Нет задач на указанную(ые) дату(ы)')
    captured_output.truncate(0)
    captured_output.seek(0)

    with requests_mock.mock() as m:
        m.get(cfg['server_url'] + '/tasks', json=[{'due_date': '2010-10-10', 'title': 'Write test'},
                                                  {'due_date': '2010-10-10', 'title': 'Cry'},
                                                  {'due_date': '2010-10-11', 'title': 'Do not print'}])
        main.main.tasks_getting_command(msg)
    assert captured_output.getvalue().__contains__('Write test')
    assert captured_output.getvalue().__contains__('Cry')
    assert not captured_output.getvalue().__contains__('Do not print')
    captured_output.truncate(0)
    captured_output.seek(0)

    with requests_mock.mock() as m:
        m.get(cfg['server_url'] + '/tasks', exc=ValueError)
        main.main.tasks_getting_command(msg)
    assert captured_output.getvalue().__contains__('Потеряно соединение с сервером')
    captured_output.truncate(0)
    captured_output.seek(0)


def check_command_as_credentials(msg, captured_output):
    func = None
    if msg.text.__contains__('/start'):
        func = main.main.start_message
    elif msg.text.__contains__('/help'):
        func = main.main.help_command
    elif msg.text.__contains__('/schedule'):
        func = main.main.schedule_getting_command
    elif msg.text.__contains__('/tasks'):
        func = main.main.tasks_getting_command

    main.main.users_current_state[user_id] = st.States.LOGIN_ENTERING
    func(msg)
    assert captured_output.getvalue().__contains__('Команда не может быть логином. Попробуйте снова')
    captured_output.truncate(0)
    captured_output.seek(0)

    main.main.users_current_state[user_id] = st.States.PASSWORD_ENTERING
    func(msg)
    assert captured_output.getvalue().__contains__('Команда не может быть паролем. Попробуйте снова')
    captured_output.truncate(0)
    captured_output.seek(0)
