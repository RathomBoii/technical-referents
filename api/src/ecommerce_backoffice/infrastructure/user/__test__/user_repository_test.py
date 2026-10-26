import os
from datetime import date
from uuid import uuid4

from ecommerce_backoffice.infrastructure.config import construct_db_url
import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ecommerce_backoffice.domain.user.entity.user import User
from ecommerce_backoffice.domain.user.user_value_object import Email
from ecommerce_backoffice.infrastructure.user.model.user_model import Base
from ecommerce_backoffice.infrastructure.user.repository.user_repository import UserRepository


"""
Note: `sqlalchemy` can work with either Postgres or MySQL; the repository code stays the same.
To switch to MySQL, change:
- DATABASE_URL (`postgresql+psycopg://...` => `mysql+pymysql://...`)
- the installed driver (`psycopg` => `pymysql`)
MySQL also needs an explicit length on `str` columns such as `email` (e.g. `String(255)`).
"""

"""
scope="session" => the engine and the `users` table are created once per pytest run and dropped after the last test
"""
@pytest.fixture(scope="session")
def engine():
    TEST_DB_PREFIX = "TEST_DB"
    engine = create_engine(construct_db_url(TEST_DB_PREFIX))
    # ⬇️ Models were already registered in `Base.metadata` when `user_model` was imported
    Base.metadata.create_all(engine) # connect to the database, then CREATE TABLE for tables that do not exist yet
    yield engine # hand the engine to the tests; execution resumes here after the last test finishes
    Base.metadata.drop_all(engine) # runs once, after all tests are done
    engine.dispose() # close every pooled connection

"""
Open a new database session for every test case, and roll it back when the test is done.
The repository only flushes (never commits), so the rollback leaves the DB clean for the next test.
"""
@pytest.fixture
def repo(engine):
    with Session(engine) as session:
        yield UserRepository(session) # the test runs while paused here
        session.rollback() # runs after each test (even a failed one): undo the flushed, uncommitted changes


def make_user(email: str = "a@b.co") -> User:
    return User(email=Email(email), date_of_birth=date(1990, 1, 1), firstname="A", lastname="B")


def test_save_then_find(repo):
    user = make_user()
    repo.save(user)
    assert repo.find_one_by_id(user.id) == user


def test_find_missing_returns_none(repo):
    assert repo.find_one_by_id(uuid4()) is None


def test_delete_returns_user_and_removes(repo):
    user = make_user()
    repo.save(user)
    assert repo.delete(user.id) == user
    assert repo.find_one_by_id(user.id) is None


def test_delete_missing_returns_none(repo):
    assert repo.delete(uuid4()) is None


def test_duplicate_email_raises(repo):
    repo.save(make_user())
    with pytest.raises(IntegrityError):
        repo.save(make_user())
