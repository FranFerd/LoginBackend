import random

class CodeGenerator:
    @staticmethod
    def generate_code(length: int = 6):
        code = [str(random.randint(0, 9)) for _ in range(length)]
        return ''.join(code)