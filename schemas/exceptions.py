class DatabaseError(Exception):
    pass

class UserAlreadyExistsError(Exception):
    pass

class UserNotFound(Exception):
    pass