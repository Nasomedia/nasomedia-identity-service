from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session
from datetime import timedelta

from app import crud, models, schemas, deps, utils
from app.core.config import settings


router = APIRouter()


@router.get("", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
    *,
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve users.
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.get("/me", response_model=schemas.User)
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Get current user.
    """
    return current_user


@router.post("", response_model=schemas.User)
async def create_user(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
    cash_service: deps.CashService = Depends(),
    *,
    user_in: schemas.UserCreate,
):
    """
    Create new user.
    """
    user = crud.user.get_with_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.")
    user = crud.user.create(db, obj_in=user_in)
    if settings.EMAILS_ENABLED and user_in.email:
        utils.send_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
    token= utils.create_access_token(
        user.id, 
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    await cash_service.create_consumer(token)
    return user


@router.post("/open", response_model=schemas.User)
async def create_user_open(
    db: Session = Depends(deps.get_db),
    cash_service: deps.CashService = Depends(),
    *,
    password: str = Body(...),
    email: EmailStr = Body(...),
    nickname: str = Body(None),
):
    """
    Create new user without the need to be logged in.
    """
    if not settings.USERS_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=403,
            detail="Open user registration is forbidden on this server",
        )
    user = crud.user.get_with_email(db, email=email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
        
    if len(nickname) > 13:
        raise HTTPException(
            status_code=400,
            detail="Too long nickname.",
        )

    user_in = schemas.UserCreate(password=password, email=email, nickname=nickname)
    user = crud.user.create(db, obj_in=user_in)
    token= utils.create_access_token(
        user.id, 
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    await cash_service.create_consumer(token)
    return user


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_active_superuser),
    *,
    user_id: int,
    user_in: schemas.UserUpdate,
):
    """
    Update a user.
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.put("/me", response_model=schemas.User)
def update_user_me(
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_active_user),
    *,
    password: str = Body(None),
    nickname: str = Body(None),
    email: EmailStr = Body(None),
):
    """
    Update own user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if nickname is not None:
        user_in.nickname = nickname
    if email is not None:
        user_in.email = email
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user