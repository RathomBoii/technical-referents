from dataclasses import dataclass
from uuid import UUID

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
class GetUserInput:
    user_id: UUID


class GetUser:
    def __init__(self, repo: UserRepositoryPort):
        self.repo = repo
        
    def execute(self, get_user_input: GetUserInput) -> User | None:
        user = self.repo.find_one_by_id(get_user_input.user_id) 
        if not user:
            return None
        return user
        
        
        