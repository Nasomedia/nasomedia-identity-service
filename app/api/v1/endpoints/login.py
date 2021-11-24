from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, models, schemas, deps, utils
from app.core import security
from app.core.config import settings
from app.schemas.user import UserUpdate
from app.utils import (
    send_reset_password_email,
    verify_password_reset_token,
)

router = APIRouter()


@router.post("/access-token", response_model=schemas.Token)
def login_access_token(
    db: Session = Depends(deps.get_db), 
    form_data: OAuth2PasswordRequestForm = Depends(),
    security: deps.Security = Depends(deps.Security),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.user.get_with_email(db, email=form_data.username)
    if not user: # 아이디 확인
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if security.verify_password(form_data.password, user.hashed_password): # 비밀번호 확인
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        ),
        "token_type": "bearer",
    }


@router.post("/forget", response_model=schemas.Msg)
def forget_password(
    db: Session = Depends(deps.get_db),
    security: deps.Security = Depends(deps.Security),
    *,
    email: str = Body(...)
) -> Any:
    """
    Request to reset password
    """
    user = crud.user.get_with_email(db, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    utils.send_reset_password_email(
        email_to=user.email,
        email=user.email,
        token=security.generate_password_reset_token(email)
    )
    
    return {"msg": "Password updated successfully"}


@router.post("/reset", response_model=schemas.Msg)
def reset_password(
    db: Session = Depends(deps.get_db),
    user: schemas.User = Depends(deps.get_user_with_reset_token),
    *,
    new_password: str = Body(...)
) -> Any:
    """
    Reset password
    """
    crud.user.update(db, db_obj=user, password=UserUpdate(password=new_password))
    return {"msg": "Password updated successfully"}
