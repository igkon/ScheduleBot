import pytest
import requests_mock

import io
import sys

import main.main
from main.bot_config import config as cfg

import util.mocks
import util.state as st
import util.date_functions

# Test vars
main.main.tb = util.mocks.TelebotMock()
user_id = 1


@pytest.fixture(autouse=True)
def run_around_tests():

    yield

    main.main.users_current_state.clear()
    main.main.users_login.clear()
    main.main.users_password.clear()


def test_success_login_scenario():
    captured_output = io.StringIO()
    sys.stdout = captured_output

    msg = util.mocks.MessageMock('/start', user_id)

    main.main.start_message(msg)
    assert main.main.users_current_state[user_id] == st.States.LOGIN_ENTERING

    msg.text = 'login'
    main.main.authorization_finite_automate(msg)
    assert main.main.users_current_state[user_id] == st.States.PASSWORD_ENTERING

    msg.text = 'password'
    with requests_mock.mock() as m:
        m.get(cfg['server_url'] + '/tasks', text='data', status_code=200)
        main.main.authorization_finite_automate(msg)
    assert main.main.users_current_state[user_id] == st.States.AUTHORIZED

    msg.text = '/help'
    main.main.help_command(msg)
    assert captured_output.getvalue().__contains__(cfg['help_message'])

    msg.text = '/schedule 11.10.2010'
    main.main.users_current_state[user_id] = st.States.AUTHORIZED
    with requests_mock.mock() as m:
        m.get(cfg['server_url'] + '/schedule/2010-10-11', json=[])
        main.main.schedule_getting_command(msg)
    assert captured_output.getvalue().__contains__('На дату 11.10.2010 нет задач')

    msg.text ='/schedule 10.10.2010 '
    with requests_mock.mock() as m:
        m.get(cfg['server_url'] + '/schedule/2010-10-10', json=[{'subject':{'title': 'Programming'}},
                                                            {'subject':{'title': 'Math'}}])
        main.main.schedule_getting_command(msg)
    assert captured_output.getvalue().__contains__('1. Programming')
    assert captured_output.getvalue().__contains__('2. Math')
    captured_output.truncate(0)
    captured_output.seek(0)

    msg.text = '/schedule 09.10.2010-10.10.2010'
    with requests_mock.mock() as m:
        m.get(cfg['server_url'] + '/schedule/2010-10-09', json=[{'subject':{'title': 'Ph. education'}},
                                                                {'subject':{'title': 'English'}}])
        m.get(cfg['server_url'] + '/schedule/2010-10-10', json=[{'subject':{'title': 'Programming'}},
                                                                {'subject':{'title': 'Math'}}])
        main.main.schedule_getting_command(msg)
    assert captured_output.getvalue().__contains__('Расписание на 09.10.2010')
    assert captured_output.getvalue().__contains__('1. Ph. education')
    assert captured_output.getvalue().__contains__('2. English')
    assert captured_output.getvalue().__contains__('Расписание на 10.10.2010')
    assert captured_output.getvalue().__contains__('1. Programming')
    assert captured_output.getvalue().__contains__('2. Math')
    captured_output.truncate(0)
    captured_output.seek(0)

    msg.text = '/tasks 10.10.2010'
    with requests_mock.mock() as m:
        m.get(cfg['server_url'] + '/tasks', json=[{'due_date': '2010-10-09'}, {'due_date': '2010-10-08'}])
        main.main.tasks_getting_command(msg)
    assert captured_output.getvalue().__contains__('Нет задач на указанную(ые) дату(ы)')

    msg.text = '/tasks 08.10.2010'
    with requests_mock.mock() as m:
        m.get(cfg['server_url'] + '/tasks', json=[{'due_date': '2010-10-08', 'title': 'Write test'},
                                                  {'due_date': '2010-10-08', 'title': 'Cry'},
                                                  {'due_date': '2010-10-09', 'title': 'Do not print'}])
        main.main.tasks_getting_command(msg)
    assert captured_output.getvalue().__contains__('Write test')
    assert captured_output.getvalue().__contains__('Cry')
    assert not captured_output.getvalue().__contains__('Do not print')
    captured_output.truncate(0)
    captured_output.seek(0)

    msg.text = '/tasks 08.10.2010-09.10.2010'
    with requests_mock.mock() as m:
        m.get(cfg['server_url'] + '/tasks', json=[{'due_date': '2010-10-08', 'title': 'Write test'},
                                                  {'due_date': '2010-10-08', 'title': 'Cry'},
                                                  {'due_date': '2010-10-09', 'title': 'Do not print'}])
        main.main.tasks_getting_command(msg)
    assert captured_output.getvalue().__contains__('Write test')
    assert captured_output.getvalue().__contains__('Cry')
    assert captured_output.getvalue().__contains__('Do not print')


def test_failed_login():
    captured_output = io.StringIO()
    sys.stdout = captured_output

    msg = util.mocks.MessageMock('/start', user_id)

    main.main.start_message(msg)
    assert main.main.users_current_state[user_id] == st.States.LOGIN_ENTERING

    msg.text = 'login'
    main.main.authorization_finite_automate(msg)
    assert main.main.users_current_state[user_id] == st.States.PASSWORD_ENTERING

    msg.text = 'password'
    with requests_mock.mock() as m:
        m.get(cfg['server_url'] + '/tasks', text='data', status_code=404)
        main.main.authorization_finite_automate(msg)
    assert main.main.users_current_state[user_id] == st.States.LOGIN_ENTERING

    msg.text = 'login'
    main.main.authorization_finite_automate(msg)
    assert main.main.users_current_state[user_id] == st.States.PASSWORD_ENTERING

    msg.text = 'another_password'
    with requests_mock.mock() as m:
        m.get(cfg['server_url'] + '/tasks', text='data', status_code=200)
        main.main.authorization_finite_automate(msg)
    assert main.main.users_current_state[user_id] == st.States.AUTHORIZED
