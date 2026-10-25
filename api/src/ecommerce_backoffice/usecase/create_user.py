from dataclasses import dataclass
from datetime import date

from ecommerce_backoffice.domain.user.entity.user import User
from ecommerce_backoffice.domain.user.port.user_repository_port import UserRepositoryPort
from ecommerce_backoffice.domain.user.user_value_object import Email

"""
@dataclass rautomatically create these following class methods
- __init__(): Recieve value and configure class's properties
- __repr__(): Display Class's datail when execute print()
- __eq__(): Compare the property values between 2 classes
"""

"""
frozen = True
- Make class to be immutable, you can not change it's property value after initiate this class
"""


@dataclass(frozen=True)
class CreateUserInputs:
    email: Email
    date_of_birth: date
    firstname: str
    lastname: str
    middlename: str | None = None


class CreateUser:
    def __init__(self, repo: UserRepositoryPort):
        self.repo = repo
        
    def execute(self, create_user_inputs: CreateUserInputs) -> User:

        user = User(
            email=create_user_inputs.email,
            date_of_birth=create_user_inputs.date_of_birth,
            firstname=create_user_inputs.firstname,
            lastname=create_user_inputs.lastname,
            middlename=create_user_inputs.middlename,
        )

        return self.repo.save(user)
        
        
        