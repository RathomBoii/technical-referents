from ecommerce_backoffice.domain.user.user_value_object import InvalidUserError
from fastapi import FastAPI, Request
from ecommerce_backoffice.controller.user_controller import router
from ecommerce_backoffice.infrastructure.db import engine
from ecommerce_backoffice.infrastructure.user.model.user_model import Base
from fastapi.responses import JSONResponse

# Create User table
Base.metadata.create_all(engine)

app = FastAPI()
app.include_router(router)

# By define this exeptional handler at main level, this will catch all below level
# which return this error InvalidUserError before return to client
@app.exception_handler(InvalidUserError)
def invalid_user(request: Request, exc: InvalidUserError):
    return JSONResponse(status_code=422, content={"field": exc.field, "reason": exc.reason})