from sqlalchemy import create_engine, Column, Integer, LargeBinary, URL, String, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship, Mapped

url = URL.create(
    "postgresql",
    username="dbuser",
    password="dbpassword",
    port=5432,
    host="postgres-service",
    database="db"
)

engine = create_engine(url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username: Mapped[str] = Column(unique=True)
    plate_number = Column(String(7))
    posts: Mapped[list["Post"]] = relationship(back_populates="user")
    pictured: Mapped[list["Post"]] = relationship(back_populates="pictured_user")
    average_score: Mapped[float] = Column()
    name: Mapped[str] = Column()

class Post(Base):
    __tablename__ = "posts"
    image = Column(LargeBinary, nullable=False)
    id = Column(Integer, primary_key=True, index=True)
    user: Mapped["User"] = relationship(back_populates="posts")  # user who posted
    user_id: Mapped[int] = Column(ForeignKey("users.id"))  # user who posted
    score: Mapped[int] = Column()
    pictured_user: Mapped["User"] = relationship(back_populates="pictured")  # user who is in the picture
    pictured_plate_number: Mapped[str] = Column(String(7))  # license plate number in the picture

Base.metadata.create_all(bind=engine)