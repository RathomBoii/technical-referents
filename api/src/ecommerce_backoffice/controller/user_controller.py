from uuid import UUID

from ecommerce_backoffice.controller.dto.user_dto import CreateUserRequest, UserResponse
from ecommerce_backoffice.infrastructure.db import get_session
from ecommerce_backoffice.infrastructure.user.repository.user_repository import UserRepository
from ecommerce_backoffice.usecase.create_user import CreateUser
from ecommerce_backoffice.usecase.delete_user import DeleteUser, DeleteUserInput
from ecommerce_backoffice.usecase.get_user import GetUserById, GetUserByIdInput
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users", tags=["users"])

def get_repo(session: Session = Depends(get_session, scope="function")) -> UserRepository:
    return UserRepository(session)

@router.post("", status_code=201, response_model= UserResponse)
def create_user(request_body: CreateUserRequest, repo: UserRepository = Depends(get_repo)):
    usecase = CreateUser(repo)
    create_user_response = usecase.execute(
        create_user_inputs=request_body.to_usecase()
    )
    return UserResponse.from_entity(create_user_response)

@router.get("/{user_id}", status_code=200, response_model= UserResponse)
def get_user_by_id(user_id: UUID, repo: UserRepository = Depends(get_repo)):
    usecase = GetUserById(repo)
    user = usecase.execute(
        GetUserByIdInput(user_id= user_id)
    )
    
    if not user: 
        raise HTTPException(404, "user not found")
    return UserResponse.from_entity(user)

@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: UUID, repo: UserRepository = Depends(get_repo)):
    usecase = DeleteUser(repo)
    delete_user_response = usecase.execute(
        DeleteUserInput(user_id=user_id)
    )
    
    if not delete_user_response:
        raise HTTPException(404, "user not found")
    return UserResponse.from_entity(delete_user_response)