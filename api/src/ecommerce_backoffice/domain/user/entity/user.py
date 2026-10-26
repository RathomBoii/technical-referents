from datetime import datetime, date
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from ..user_value_object import InvalidUserError, Email

MIN_AGE = 18

# ใช้ @dataclass ให้ Python สร้าง __init__ จาก annotation
# __init__ เทียบเท่ากับ constructor ใน Typescript
@dataclass
class User():
    email: Email
    date_of_birth: date
    firstname: str
    lastname: str
    middlename: str | None = None
    
    id: UUID = field(default_factory=uuid4)
    create_date: datetime = field(init=False)
    age: int = field(init=False)
    fullname: str = field(init=False)
    
    def __post_init__(self):
        if not self.firstname.strip():
            raise InvalidUserError("firstname", self.firstname, "firstname required.")
        if not self.lastname.strip():
            raise InvalidUserError("lastname", self.lastname, "lastname required.")
        
        self.age = self._calculate_age()
        
        if self.age < MIN_AGE:
            raise InvalidUserError("date_of_birth", self.date_of_birth, "user's age must equal or more than 18 years old.")
        
        self.fullname = self._construct_fullname()
        self.create_date = datetime.now()
        
        
    def _calculate_age(self) -> int:
        today = date.today()
        had_birthday = (today.month, today.day) >= (self.date_of_birth.month, self.date_of_birth.day)
        return today.year - self.date_of_birth.year - (not had_birthday)
        
    def _construct_fullname(self) -> str:
        return " ".join(p for p in (self.firstname, self.middlename, self.lastname) if p)
    
    