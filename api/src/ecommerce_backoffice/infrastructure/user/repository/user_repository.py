from sqlalchemy.orm import Session
from uuid import UUID

from ecommerce_backoffice.domain.user.entity.user import User
from ecommerce_backoffice.domain.user.port.user_repository_port import UserRepositoryPort
from ecommerce_backoffice.infrastructure.user.model.user_model import UserRow


class UserRepository(UserRepositoryPort):
    def __init__(self, session: Session):
        self.session = session
    
    def save(self, user: User) -> User:
        user_row = UserRow._to_row(user)
        self.session.add(user_row)
        # flush ส่ง SQL ไป DB แต่ไม่ commit: ผู้สร้าง session เป็นคนกำหนดขอบเขต transaction (commit/rollback)
        self.session.flush()
        return user

    def find_one_by_id(self, user_id: UUID) -> User | None:
        user_row = self.session.get(UserRow, user_id)
        return user_row._to_entity() if user_row else None

    def delete(self, user_id: UUID) -> User | None:
        user_row = self.session.get(UserRow, user_id)
        if not user_row:
            return None
        deleted_user = user_row._to_entity()
        self.session.delete(user_row)
        self.session.flush()
        return deleted_user