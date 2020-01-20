from enum import Enum


class States(Enum):
    #INITIAL = 0 # Before /start command
    LOGIN_ENTERING = 1 # Bot asks about login
    PASSWORD_ENTERING = 2 # Bot asks about password
    AUTHORIZED = 3 # User is authorized. User can interact with schedule and tasks
