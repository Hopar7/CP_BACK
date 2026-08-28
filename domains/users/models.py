from sqlalchemy import Column, String, Integer, LargeBinary, func, DateTime,ForeignKey
from typing import Optional
from sqlalchemy.types import BLOB
import datetime
from dependencies.database import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nick_name = Column(String, nullable=False)
    name = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    checked = Column(String,nullable=True)
    month = Column(Integer, nullable=True)
    cash = Column(Integer,default=0)
    kakaoid = Column(String, nullable=True)
    deals = Column(Integer,default=0)
    sales = Column(Integer,default=0)
    totalscore = Column(Integer, default=0)
    purchase_count = Column(Integer, default=0)  # 구매 횟수
    sales_count = Column(Integer, default=0)  # 판매 횟수
    

class ContentModel(Base):    # 글 작성 테이블
    __tablename__ = "contents"
    id = Column(Integer, primary_key=True, autoincrement=True)
    userid = Column(String, nullable=False)
    title = Column(String, nullable=False)
    text = Column(String, nullable=False)
    startprice = Column(Integer, nullable=False)
    picture = Column(String, nullable=False)
    view_count = Column(Integer, default=0)
    recommend = Column(Integer, default=0)
    start_time = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    bidder = Column(String, nullable=True)
    price_info = Column(String, nullable=True)
    like_count = Column(Integer, default=0)
    tag = Column(String, default="없음")
    state = Column(String, default="판매 중")

class LikeModel(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False)
    content_id = Column(Integer, nullable=False) 