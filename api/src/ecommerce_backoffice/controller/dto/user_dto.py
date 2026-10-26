from datetime import date
from uuid import UUID

from ecommerce_backoffice.domain.user.entity.user import User

from ecommerce_backoffice.usecase.create_user import CreateUserInputs
from ecommerce_backoffice.domain.user.user_value_object import Email
from pydantic import BaseModel

"""
BaseModel automatically validate the input data's type acording to 
the class's property type we define.
"""
class CreateUserRequest(BaseModel):
    email: str
    date_of_birth: date
    firstname: str
    lastname: str
    middlename: str | None = None
    
    def to_usecase(self) -> CreateUserInputs:
        return CreateUserInputs(
            email= Email(self.email),
            date_of_birth= self.date_of_birth,
            firstname= self.firstname,
            lastname= self.lastname,
            middlename= self.middlename
        )

class UserResponse(BaseModel):
    id: UUID
    email: str
    fullname: str    
    age: int
    
    @classmethod
    def from_entity(cls, user: User) -> UserResponse:
        return cls(
            id= user.id,
            email= user.email.value,
            fullname=user.fullname,
            age=user.age
        )
