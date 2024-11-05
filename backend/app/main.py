from fastapi import FastAPI, Depends, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import SessionLocal
from auth import login_google, auth_google, set_user_info, refresh_token, get_user_id, get_user_info
from posts import create_post, get_post, get_post_info, get_user_posts, get_recent_post_id

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/login/google")
async def login_google_route():
    return await login_google()


@app.get("/auth/google")
async def auth_google_route(code: str, db: Session = Depends(get_db)):
    return await auth_google(code, db)

@app.get("/auth/get_user_id")
async def get_user_id_route(token: str = Depends(oauth2_scheme)):
    return await get_user_id(token)


@app.post("/user/{user_id}")
async def set_user_info_route(user_id: int, username: str = None, plate_number: str = None,
                              db: Session = Depends(get_db),
                              token: str = Depends(oauth2_scheme)):
    return await set_user_info(user_id, username, plate_number, db, token)


@app.get("/users/get_user_info/{user_id}")
async def get_user_info_route(user_id: int, db: Session = Depends(get_db)):
    return await get_user_info(user_id, db)


@app.post("/posts/")
async def create_post_route(file: UploadFile = File(...), db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    return await create_post(file, db, token)


@app.get("/token")
async def get_token_route(token: str = Depends(oauth2_scheme)):
    return {"token": token}


@app.get("/posts/{post_id}")
async def get_post_route(post_id: int, db: Session = Depends(get_db)):
    return await get_post(post_id, db)


@app.get("/posts/info/{post_id}")
async def get_post_info_route(post_id: int, db: Session = Depends(get_db)):
    return await get_post_info(post_id, db)


@app.get("/posts/user/{user_id}")
async def get_user_posts_route(user_id: int, db: Session = Depends(get_db)):
    return await get_user_posts(user_id, db)


@app.get("/posts/recent_id")
async def get_recent_post_id_route(db: Session = Depends(get_db)):
    return await get_recent_post_id(db)


@app.post("/refresh_token")
async def refresh_token_route(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return await refresh_token(token, db)
