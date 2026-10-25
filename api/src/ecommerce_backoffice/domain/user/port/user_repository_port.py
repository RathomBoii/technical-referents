from abc import ABC, abstractmethod
from uuid import UUID

from ecommerce_backoffice.domain.user.entity.user import User


# ⬇️ Because Exception error can handle any error from database, so define this as is is enough
# class repositoryError(Exception):

# ⬇️ Because duplicated user is can be considerred as the business logic, so create it's error instance is make sense here
# class DuplicatedUserError(RepositoryError)
    

class UserRepositoryPort(ABC):
    @abstractmethod
    def save(self, user: User) -> User: ...
    
    @abstractmethod
    def delete(self, user_id: UUID) -> User | None: ...

    @abstractmethod
    def find_one_by_id(self, user_id: UUID) -> User | None: ...