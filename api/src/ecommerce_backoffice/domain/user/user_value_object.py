from dataclasses import dataclass
import re

_EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")

class InvalidUserError(ValueError):
    def __init__(self, field: str, value: object, reason: str):
        self.field = field
        self.value = value
        self.reason = reason
        # above ⬆️: we are overide the super class `ValueError`'s __init__
        # below ⬇️: we call `ValueError`'s __init__ and pass the `InvalideUserError`'s argument to it
        super().__init__(f"Invalid {field} {value}: {reason}")

@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if not _EMAIL.fullmatch(self.value):
            raise InvalidUserError("email", self.value, "invalid format")

        
