import pytest

import datetime
import io
import sys

from util.date_functions import convert_date_list_to_date_object
from util.date_functions import get_date_list
from util.date_functions import parse_command_date

from util.date_range_exception import DateRangeException
from util.mocks import TelebotMock
from util.mocks import MessageMock


# Happy path of converting date from the list to the datetime object
def test_convert_date_list_to_date_object():
    date_list = [31, 1, 2013]
    data_object = convert_date_list_to_date_object(date_list)
    example = datetime.date(int(date_list[2]), int(date_list[1]), int(date_list[0]))
    assert str(example) == str(data_object)


# Test list length error
def test_convert_date_wrong_length():
    with pytest.raises(IndexError):
        date_list = [31, 1]
        data_object = convert_date_list_to_date_object(date_list)
        example = datetime.date(int(date_list[2]), int(date_list[1]), int(date_list[0]))
        assert str(example) == str(data_object)


# Test wrong date list
def test_convert_date_wrong_date_list():
    with pytest.raises(ValueError):
        date_list = [32, 1, 2013]
        data_object = convert_date_list_to_date_object(date_list)
        example = datetime.date(int(date_list[2]), int(date_list[1]), int(date_list[0]))
        assert str(example) == str(data_object)


# Happy path get_date_list
def test_get_date_list():
    correct_range = '12.12.2012-14.12.2012'
    check_list = [datetime.date(2012,12,12), datetime.date(2012,12,13), datetime.date(2012,12,14)]
    got_list = get_date_list(correct_range)
    assert got_list == check_list


# Test get_date_list with range having more than one '-'
def test_get_date_list_triple_range():
    with pytest.raises(IndexError):
        triple_range = '12.12.2012-15.12.2012-20.12.2012'
        get_date_list(triple_range)


# Test get_date_list with wrong range
def test_get_date_list_wrong_range_format():
    with pytest.raises(ValueError):
        wrong_range_month = '12.13.2012-15.13.2012'
        get_date_list(wrong_range_month)
        wrong_range_day = '29.12.2012-32.12.2012'
        get_date_list(wrong_range_day)
        wrong_range_random = 'fsdgfg-fgdfgsfsd'
        get_date_list(wrong_range_random)


# Test get_date_list with too big range (more than 7 days)
def test_get_date_list_too_big_range():
    with pytest.raises(DateRangeException):
        big_range = '12.12.2012-20.12.2012'
        get_date_list(big_range)


# Test get_date_list with negative range
def test_get_date_list_negative_range():
    with pytest.raises(DateRangeException):
        big_range = '12.12.2012-10.12.2012'
        get_date_list(big_range)


def test_parse_command_date_success_single():
    tb = TelebotMock()
    msg = MessageMock('/schedule 12.12.2012', 1)
    check = [datetime.date(2012,12,12)]
    got = parse_command_date(tb, msg)
    assert got == check


def test_parse_command_date_success_range():
    tb = TelebotMock()
    msg = MessageMock('/schedule 12.12.2012-14.12.2012', 1)
    check = [datetime.date(2012,12,12), datetime.date(2012,12,13), datetime.date(2012,12,14)]
    got = parse_command_date(tb, msg)
    assert got == check


def test_parse_command_date_without_date():
    captured_output = io.StringIO()
    sys.stdout = captured_output
    tb = TelebotMock()
    msg = MessageMock('/schedule', 1)
    parse_command_date(tb, msg)
    sys.stdout = sys.__stdout__
    assert captured_output.getvalue() == 'User 1 sent message: Введите дату/даты корректно. Для подробной информации используйте /help\n'


def test_parse_command_date_without_wrong_range():
    captured_output = io.StringIO()
    sys.stdout = captured_output
    tb = TelebotMock()
    msg = MessageMock('/schedule 12.12.2012-21.12.2012', 1)
    parse_command_date(tb, msg)
    sys.stdout = sys.__stdout__
    assert captured_output.getvalue() == 'User 1 sent message: Неподдерживаемый промежуток между датами. Число дней > 7 или < 0\n'


def test_parse_command_date_without_wrong_date():
    captured_output = io.StringIO()
    sys.stdout = captured_output
    tb = TelebotMock()
    msg = MessageMock('/schedule 12.13.2012', 1)
    parse_command_date(tb, msg)
    sys.stdout = sys.__stdout__
    assert captured_output.getvalue() == 'User 1 sent message: Введите дату/даты корректно. Для подробной информации используйте /help\n'


def test_data_range_exception():
    exc = DateRangeException()
    assert exc.__str__() == 'DateRangeException range > 7 or < 0'







