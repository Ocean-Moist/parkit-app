import os
from datetime import datetime, timedelta, timezone as tz
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
import requests
from fastapi.responses import RedirectResponse

from database import User, SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Replace these with your own values from the Google Developer Console
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def login_google():
    return RedirectResponse(
        url=f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&scope=openid%20profile%20email&access_type=offline")


async def auth_google(code: str, db: Session = Depends(get_db)):
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=data)
    access_token = response.json().get("access_token")
    user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo",
                             headers={"Authorization": f"Bearer {access_token}"}).json()

    if user_info["hd"] != "athenian.org":
        raise HTTPException(status_code=400, detail="Only Athenian emails are allowed")

    user = db.query(User).filter(User.email == user_info["email"]).first()
    if not user:
        email = user_info["email"]
        user = User(
            email=email, username=email.split("@")[0] + str(hash(email)), plate_number=0, average_score=0.0,
            name=user_info["name"])
        db.add(user)
        db.commit()
        db.refresh(user)

    return await generate_token(user)


async def generate_token(user):
    expire_time = datetime.now(tz.utc) + timedelta(minutes=30)
    token_payload = {
        "sub": str(user.id),
        "email": user.email,
        "exp": expire_time
    }
    token = jwt.encode(token_payload, GOOGLE_CLIENT_SECRET, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}


async def set_user_info(user_id: int, username: str = None, plate_number: str = None, db: Session = Depends(get_db),
                        token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, GOOGLE_CLIENT_SECRET, algorithms=["HS256"])
    user_email = payload["email"]

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.email != user_email:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")

    if username is not None:
        user.username = username
    if plate_number is not None:
        user.plate_number = plate_number

    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "plate_number": user.plate_number
    }


async def get_user_info(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "plate_number": user.plate_number,
        "name": user.name
    }


async def get_user_id(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, GOOGLE_CLIENT_SECRET, algorithms=["HS256"])
    return payload["sub"]


async def refresh_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, GOOGLE_CLIENT_SECRET, algorithms=["HS256"])
        user_id = payload["sub"]
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return generate_token(user)
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")
