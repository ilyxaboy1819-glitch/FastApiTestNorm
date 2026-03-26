class ValidationException(Exception):
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
