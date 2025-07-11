from argon2 import PasswordHasher

class Argon2Ph:
    def __init__(self):
        self.ph = PasswordHasher()

    def hash_password(self, password: str) -> str:
        return self.ph.hash(password)

    def verify_password(self, hashed_password: str, password: str) -> bool:
        try:
            return self.ph.verify(hash=hashed_password, password=password)
        except:
            return False
# Another way to do it. Supports multiple schemes -> switching is easy. Use the first, if committed to Argon2 only.
# from passlib.context import CryptContext

# pwd_context = CryptContext(
#     schemes=["argon2"],
#     default="argon2",
#     deprecated="auto"
# )

# def hash_password(password: str) -> str:
#     return pwd_context.hash(password)

# def verify_password(plain_password: str, hashed_password: str | None) -> bool:
#     return pwd_context.verify(plain_password, hashed_password) 