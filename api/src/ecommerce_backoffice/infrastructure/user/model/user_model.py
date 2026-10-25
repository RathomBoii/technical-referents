from datetime import date, datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from uuid import UUID

from ecommerce_backoffice.domain.user.entity.user import User
from ecommerce_backoffice.domain.user.user_value_object import Email

# ⬇️ Create base class for every ORM model which inherit from DeclarativeBase class from sqlalchemy Lib
# ⬇️ The `...` mean there are no need any additional logic because all property, method, etc are already comes from `DeclarativeBase`
"""⬇️ DeclarativeBase register Base class into Python memory 
    - ✅ Define the model's schema once, and use this base class on all database operation
    - ✅ Execute database operation without writing the SQL, only using Python syntax
    - ✅ Response from database automatically converted into UserRow
"""
class Base(DeclarativeBase): ...

class UserRow(Base):
    __tablename__ = "users"
    
    id: Mapped[UUID] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    date_of_birth: Mapped[date]
    firstname: Mapped[str]
    lastname: Mapped[str]
    middlename: Mapped[str | None]
    create_date: Mapped[datetime]
    
    # ⬇️ This decorator make this method callable withou any UserRow class's instance
    @classmethod
    def _to_row(cls, user: User) -> UserRow:
        return cls(
            id = user.id,
            email = user.email.value,
            date_of_birth = user.date_of_birth,
            firstname = user.firstname,
            middlename = user.middlename,
            lastname = user.lastname,
            create_date = user.create_date
        )
    
    def _to_entity(self) -> User:
            user = User(
                id = self.id,
                email = Email(self.email),
                date_of_birth = self.date_of_birth,
                firstname = self.firstname,
                middlename = self.middlename,
                lastname = self.lastname,
            )
            user.create_date = self.create_date
            return user