from datetime import datetime, timedelta
from typing import List
from sqlalchemy import update
from sqlalchemy.sql.functions import user
from fastapi import Response, Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from . import crud, models, schemas
from .database import SessionLocal, engine
from jose import JWTError, jwt
from dto.user import User
from dto.post import Post
from starlette.status import HTTP_204_NO_CONTENT, HTTP_200_OK, HTTP_401_UNAUTHORIZED

models.Base.metadata.create_all(bind=engine)


app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, crud.SECRET_KEY,
                             algorithms=[crud.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = username
    except JWTError:
        raise credentials_exception
    user = crud.get_user(db, username=token_data)
    if user is None:
        raise credentials_exception
    return user


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crud.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/")
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user


@app.post("/users/")
def create_user(
    user: schemas.UserCreate, db: Session = Depends(get_db)
):
    return crud.create_user(db=db, user=user)


@app.post("/posts/")
def create_post(
    title: str, body: str,  db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    user_id = current_user.id
    return crud.create_post(db=db, user_id=user_id, title=title, body=body)


@app.get("/posts/")
def post_list(
    db: Session = Depends(get_db), auth: models.User = Depends(get_current_user)
):
    return crud.post_list(db=db)


@app.get("/posts/{posts_id}")
def post_detail(
    posts_id: int, db: Session = Depends(get_db), auth: models.User = Depends(get_current_user)
):
    return crud.get_post(db=db, id=posts_id)


@app.put("/posts/{id}")
async def update_post(
    id: int, post: Post,  db: Session = Depends(get_db), auth: models.User = Depends(get_current_user)
):
    print(auth.id)
    isOwner = crud.check_Owner(db, auth.id, id)
    print(isOwner)
    if isOwner:
        crud.upd_post(db, id, post)
        return Response(status_code=HTTP_200_OK)
    else:
        return Response(status_code=HTTP_401_UNAUTHORIZED)


@app.delete("/posts/{id}")
def delete_post(
    post_id: int, db: Session = Depends(get_db), auth: models.User = Depends(get_current_user)
):
    isOwner = crud.check_Owner(db, auth.id, post_id)
    if isOwner:
        crud.del_post(db=db, id=post_id)
        return Response(status_code=HTTP_204_NO_CONTENT)
    else:
        return Response(status_code=HTTP_401_UNAUTHORIZED)


@app.get("/users/{users_id}")
def read_user_details(
    user_id: int, db: Session = Depends(get_db), auth: models.User = Depends(get_current_user)
):
    userModel = crud.get_user_by_id(db=db, id=user_id)
    return User(userModel)
