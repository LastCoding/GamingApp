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


app = FastAPI(
    title="GamingApp API",
    description="This is a CRUD API, to get control of your favourite video games.",
    version="0.0.1",
    openapi_tags=[{
        "name": "users",
        "description": "This section is for Create & Read users."
    },
        {
        "name": "posts",
        "description": "This section is for Create, Consult, List, Modify & Delete posts."
    }
    ])

# Dependency


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
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


@app.post("/token", response_model=schemas.Token, tags=["users"], )
async def login_for_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
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


@app.post("/users/",
          tags=["users"],
          summary="Creates a user",
          description="Creates a user with all required fields. <br> - **Username**: Each user must have a username. <br> - **Password**: You need a password to authenticate with your username. <br> - **Email**: You should add your email address to get more info about you.")
def create_user(
    user: schemas.UserCreate, db: Session = Depends(get_db)
):
    return crud.create_user(db, user)


@app.get("/users/me/",
         tags=["users"],
         summary="Shows your user info",
         description="Shows all your info, such as your: <br> - **id** <br> - **email** <br> - **hashed password** <br> - **created date** <br> - **username**")
async def read_users_me(
    current_user: models.User = Depends(get_current_user)
):
    return current_user


@app.get("/users/{user_id}",
         tags=["users"],
         summary="Shows all the info from a user of your choose",
         description="Shows all the info from a user, such as the: <br> - **id** <br> - **email** <br> - **hashed password** <br> - **created date** <br> - **username**")
def read_user_details(
    user_id: int, db: Session = Depends(get_db), auth: models.User = Depends(get_current_user)
):
    userModel = crud.get_user_by_id(db, user_id)
    return User(userModel)


@app.post("/posts/",
          tags=["posts"],
          summary="Creates a post",
          description="Create a post to register your videogame with all required fields. <br> - **Name**: The name of the videogame you want to register. <br> - **Platforms**: The compatible platforms. <br> - **Genre**: The genre of the videogame.")
def create_post(
    name: str, platforms: str, genre: str,  db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    user_id = current_user.id
    return crud.create_post(db, user_id, name, platforms, genre)


@app.get("/posts/list/",
         tags=["posts"],
         summary="Lists all the posts",
         description="Lists all the posts of videogames from all the users.")
def post_list(
    db: Session = Depends(get_db), auth: models.User = Depends(get_current_user)
):
    return crud.post_list(db=db)


@app.get("/posts/{posts_id}",
         tags=["posts"],
         summary="Shows the info from a post of your choose",
         description="Shows all the info of a certain post, such as <br> - **Name** <br> - **Platforms** <br> - **Genre**"
         )
def post_detail(
    posts_id: int, db: Session = Depends(get_db), auth: models.User = Depends(get_current_user)
):
    return crud.get_post(db, posts_id)


@app.put("/posts/{id}",
         tags=["posts"],
         summary="Updates the info of one of your posts.",
         description="Updates the info of one of your posts, you can't update it if you don't own it."
         )
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


@app.delete("/posts/{id}",
            tags=["posts"],
            summary="Deletes the info of one of your posts.",
            description="Deletes the info of one of your posts, you can't delete it if you don't own it")
def delete_post(
    id: int, db: Session = Depends(get_db), auth: models.User = Depends(get_current_user)
):
    isOwner = crud.check_Owner(db, auth.id, id)
    if isOwner:
        crud.del_post(db, id)
        return Response(status_code=HTTP_204_NO_CONTENT)
    else:
        return Response(status_code=HTTP_401_UNAUTHORIZED)
