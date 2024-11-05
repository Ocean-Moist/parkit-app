import base64
from fastapi import HTTPException, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from jose import jwt

from backend.app.parking_rating import get_image_info
from database import Post, User
from utils import get_plate_number, bytes_to_ndarray, get_bars_x
from auth import oauth2_scheme, GOOGLE_CLIENT_SECRET


async def create_post(file: UploadFile = File(...),
                      db: Session = Depends(), token: str = Depends(oauth2_scheme)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File is not an image")
    if file.size > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File is too large")

    payload = jwt.decode(token, GOOGLE_CLIENT_SECRET, algorithms=["HS256"])
    user_email = payload["email"]

    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    contents = await file.read()
    image = bytes_to_ndarray(contents)
    x_1l, x_2l = get_bars_x(image)

    plate_number = await get_plate_number(image, x_1l, x_2l)

    # get score and annotated image
    image_info = get_image_info(image, x_1l, x_2l)
    score = image_info["score"]
    image_base64 = image_info["annotated_image_base64"]

    image_bytes = base64.b64decode(image_base64)

    post = Post(image=image_bytes, user=user, pictured_plate_number=plate_number, score=score)
    db.add(post)
    db.commit()
    db.refresh(post)

    return {"id": post.id, "plate_number": plate_number, "score": score}


async def get_post(post_id: int, db: Session = Depends()):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post.image


async def get_post_info(post_id: int, db: Session = Depends()):
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Convert the image to base64 encoded string
    base64_image = base64.b64encode(post.image).decode('utf-8')

    return {
        "image": base64_image,
        "user": {
            "id": post.user.id,
            "name": post.user.name,
            "email": post.user.email,
        },
        "score": post.score,
        "picturedUser": {
            "id": post.pictured_user.id,
            "name": post.pictured_user.name,
            "email": post.pictured_user.email,
        },
        "picturedPlateNumber": post.pictured_plate_number,
    }


async def get_user_posts(user_id: int, db: Session = Depends()):
    posts = db.query(Post).join(User).filter(User.id == user_id).all()
    if not posts:
        raise HTTPException(status_code=404, detail="No posts found for the user")
    return [{"id": post.id} for post in posts]


async def get_recent_post_id(db: Session = Depends()):
    post = db.query(Post).order_by(Post.id.desc()).first()
    if not post:
        raise HTTPException(status_code=404, detail="No posts found")
    return {"id": post.id}
