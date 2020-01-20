class DateRangeException(Exception):
    def __init__(self, *args):
        pass

    def __str__(self):
        return 'DateRangeException range > 7 or < 0'
