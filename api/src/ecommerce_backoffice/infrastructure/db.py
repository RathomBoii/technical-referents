import os
from collections.abc import Iterator

from ecommerce_backoffice.infrastructure.config import construct_db_url
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine(construct_db_url())


"""Provide a database session for one unit of work (e.g. one API request).

    Think of a Session as a "shopping cart" for database changes:
    you add, update, or delete objects through it, and nothing is
    saved permanently until the cart is "checked out" (committed).

    How it works:
    - ``Session(engine)`` opens a session using the shared connection pool.
    - ``session.begin()`` starts a transaction.
    - ``yield session`` hands the session to the caller to do its work.
    - When the caller finishes without errors, the transaction is
      committed automatically (all changes are saved together).
    - If an exception is raised, the transaction is rolled back
      (no partial changes are saved).
    - Finally, the session is closed and its connection is returned
      to the pool.

    Typical usage is as a dependency (e.g. FastAPI ``Depends(get_session)``),
    so each request gets its own fresh session.
    """
def get_session() -> Iterator[Session]:
    with Session(engine) as session, session.begin():
        yield session
