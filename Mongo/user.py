import os
from datetime import datetime, timedelta, timezone
from typing import List, Annotated
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from fastapi import APIRouter, status, Form, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from Mongo.connection import database
from fastapi.responses import FileResponse, JSONResponse
from fastapi import FastAPI, Request, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import dotenv



router = APIRouter()
db = database('flashx')


SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))


templates = Jinja2Templates(directory="templates")
router.mount("/static", StaticFiles(directory="static"), name="static")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: EmailStr


class UserLogin(BaseModel):
    username: str
    password: str


class UserInDB(User):
    password: str


class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    answer: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login_user")


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def submit_register(request: Request, username: str = Form(...), email: str = Form(...),
                          password: str = Form(...)):
    msg = ""
    user = UserInDB(username=username, email=email, password=password, is_active=False)
    if await user_exists(user.username, user.email, db.get_collection('users_collection')):
        msg = "User already exist"
        return templates.TemplateResponse("register.html", {"request": request, "msg": msg})
    await add_user(user)
    msg = "Registration Successful"
    return templates.TemplateResponse("register.html", {"request": request, "msg": msg})


async def user_exists(username: str, email: str, databasedb):
    if databasedb.find_one({"username": username}):
        return True
    if databasedb.find_one({"email": email}):
        return True
    return False


async def add_user(user: UserInDB):
    hashed_password = get_password_hash(user.password)
    user.password = hashed_password
    user_id = db.get_collection('users_collection').insert_one(user.dict()).inserted_id
    return user_id


# //////////////////////////////////////////////////////////////////


async def get_user(database_collection, username: str):
    user = database_collection.find_one({"username": username})
    if user:
        return UserInDB(**user)
    else:
        return None


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def authenticate_user(database_collection, username: str, password: str):
    user = await get_user(database_collection, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    return token_data


async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Annotated[OAuth2PasswordRequestForm, Depends()
@router.post('/login')
async def login_for_access_token(user: UserLogin,  response: Response):
    user = await authenticate_user(db.get_collection('users_collection'), user.username,
                                   user.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        response.set_cookie(key="access_token", value=access_token, httponly=True)


@router.get("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
