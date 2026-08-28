from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from pydantic import BaseModel
from jose import jwt
from .config import get_config

ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
conf_vars = get_config()
secret_key = conf_vars.jwt_secret_key
jwt_expire_minutes = conf_vars.jwt_expire_minutes

class Token(BaseModel):
    token: str
    type: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()

    # JWT 토큰의 만료 시간을 설정합니다.
    expire = datetime.now(timezone.utc) + timedelta(minutes=jwt_expire_minutes)
    to_encode.update({"exp": expire})

    # JWT 토큰을 생성합니다.
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt