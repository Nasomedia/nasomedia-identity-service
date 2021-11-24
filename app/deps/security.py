from datetime import datetime, timedelta
from typing import Any, Union, Optional

from jose import jwt

from app.core.config import settings

from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = "HS256"


class Security():
    def create_access_token(
        self, 
        subject: Union[str, Any],
        expires_delta: timedelta = None
    ) -> str:
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode = {"exp": expire, "sub": str(subject)}
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def verify_password(
        self, 
        plain_password: str, 
        hashed_password: str
    ) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    def generate_password_reset_token(email: str) -> str:
        delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
        now = datetime.utcnow()
        expires = now + delta
        exp = expires.timestamp()
        encoded_jwt = jwt.encode(
            {"exp": exp, "nbf": now, "sub": email}, settings.SECRET_KEY, algorithm="HS256",
        )
        return encoded_jwt

    def verify_password_reset_token(token: str) -> Optional[str]:
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            return decoded_token["email"]
        except jwt.JWTError:
            return None    