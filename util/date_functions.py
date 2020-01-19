import datetime


def convert_date_list_to_date_object(date_list):
    if len(date_list) != 3:
        raise IndexError
    # our command format is DD.MM.YYYY
    try:
        date_object = datetime.date(int(date_list[2]), int(date_list[1]), int(date_list[0]))
        return date_object
    except ValueError:
        raise ValueError
