from datetime import date

from ecommerce_backoffice.controller.dto.user_dto import CreateUserRequest, UserResponse
from ecommerce_backoffice.domain.user.entity.user import User
from ecommerce_backoffice.domain.user.user_value_object import Email
from ecommerce_backoffice.usecase.create_user import CreateUserInputs

VALID = {"email": "a@b.co", "date_of_birth": "1990-01-01", "firstname": "A", "lastname": "B"}


def test_convert_create_user_request_to_usecase():
    # the date string "1990-01-01" will be handled by Pydantic inherit from BaseModel
    #  it convert "1990-01-01" to be date(1990, 1, 1) automatically
    request_body = CreateUserRequest(**VALID) # type: ignore

    assert request_body.to_usecase() == CreateUserInputs(
        email=Email("a@b.co"),
        date_of_birth=date(1990, 1, 1),
        firstname="A",
        lastname="B",
    )


def test_convert_user_entity_to_client_format():
    # VALID holds raw client strings, so email and date_of_birth are built explicitly here
    entity = User(
        email=Email(VALID["email"]),
        date_of_birth=date.fromisoformat(VALID["date_of_birth"]),
        firstname=VALID["firstname"],
        lastname=VALID["lastname"],
    )

    response = UserResponse.from_entity(entity)

    assert response == UserResponse(id=entity.id, email="a@b.co", fullname="A B", age=entity.age)
