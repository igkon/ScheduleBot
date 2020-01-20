import datetime
import requests
from util.date_range_exception import DateRangeException


def convert_date_list_to_date_object(date_list):
    if len(date_list) != 3:
        raise IndexError
    # our command format is DD.MM.YYYY
    try:
        date_object = datetime.date(int(date_list[2]), int(date_list[1]), int(date_list[0]))
        return date_object
    except ValueError:
        raise ValueError


def parse_command_date(tb, message):
    try:
        date = message.text.split()[1]
        if '-' in date:
            dates_after_parse = get_date_list(date)
            return dates_after_parse
        else:
            date_list = date.split('.')
            date_object = convert_date_list_to_date_object(date_list)
            dates_after_parse = [date_object]
            return dates_after_parse
    except DateRangeException:
        tb.send_message(message.chat.id, 'Неподдерживаемый промежуток между датами. Число дней > 7 или < 0')
    except IndexError:
        tb.send_message(message.chat.id, 'Введите дату/даты корректно. Для подробной информации используйте /help')
    except ValueError:
        tb.send_message(message.chat.id, 'Введите дату/даты корректно. Для подробной информации используйте /help')


def get_date_list(date_range):
    date_range_list = date_range.split('-')
    if len(date_range_list) != 2:
        raise IndexError
    date_list_left = date_range_list[0].split('.')
    date_object_left = convert_date_list_to_date_object(date_list_left)
    date_list_right = date_range_list[1].split('.')
    date_object_right = convert_date_list_to_date_object(date_list_right)
    date_delta = date_object_right - date_object_left
    # нашли разницу в днях между двумя датами
    if date_delta.days < 0 or date_delta.days > 7:
        raise DateRangeException
    else:
        request_date_list = list()
        for i in range(0, date_delta.days + 1):
            # цикл по всем датам в этом интервале. Заполняем список дат для запросов
            date_diff = datetime.timedelta(days=i)
            date_cycle = date_object_left + date_diff
            request_date_list.append(date_cycle)
        return request_date_list
