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