class DatabaseError(Exception):
    pass

class UserAlreadyExistsError(Exception):
    pass

class UserNotFound(Exception):
    pass

class InvalidTokenError(Exception):
    pass

class TokenNotFoundError(Exception):
    pass

class TokenCreationError(Exception):
    pass

class EmailSendError(Exception):
    pass