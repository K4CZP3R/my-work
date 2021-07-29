from fastapi import APIRouter, Body, HTTPException, status, Depends
from models.response import ResponseErrorModel
from typing import List
from fastapi.encoders import jsonable_encoder
from models.authenticate import RequestAuthenticateModel, TokenData, TokenModel
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional
import config

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/")


router = APIRouter(
    prefix="/auth", tags=['auth']
)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials!",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGO])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    return token_data.username
async def get_current_active_user(current_username: str = Depends(get_current_user)):
    return current_username

def authenticate_user(username: str, password: str) -> str:
    if username != config.USER_USERNAME or password != config.USER_PASSWORD:
        return None
    return username

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGO)
    return encoded_jwt


@router.post('/', response_description="Request token", response_model=TokenModel)
async def auth(model: OAuth2PasswordRequestForm = Depends()):
    username = authenticate_user(model.username, model.password)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=" Incorrect username and/or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token_expires = timedelta(minutes=15)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )

    return TokenModel(access_token=access_token, token_type="bearer")

@router.get("/me")
async def me(username: str = Depends(get_current_active_user)):
    return {"username": username}