import os
from sqlalchemy.engine import URL

def construct_db_url(prefix: str = "DB") -> URL:
    return URL.create(
        "postgresql+psycopg",
        username=os.environ[f"{prefix}_USER"],
        password=os.environ[f"{prefix}_PASSWORD"],
        host=os.environ[f"{prefix}_HOST"],
        port=int(os.environ[f"{prefix}_PORT"]),
        database=os.environ[f"{prefix}_NAME"],
    )