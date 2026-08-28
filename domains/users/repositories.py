import datetime
from sqlalchemy import and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from .models import ContentModel, UserModel,LikeModel

class UserRepository:
    def __init__(self, session: AsyncSession):
        self._session = session


    async def update_user_cash(self, *, user: UserModel, amount: float):
        user.cash += amount
        self._session.add(user)
        await self._session.commit()
        return user

    async def create_user(self, *, user_name: str, password: str, user_nick: str) -> str:
        async with self._session.begin():
            user_entity = UserModel(name=user_name, password=password, nick_name=user_nick)
            self._session.add(user_entity)
            await self._session.commit()
            return user_entity.name

    async def change_password(self, *, user_id: int, new_password: str):
        async with self._session.begin():
            query = await self._session.execute(select(UserModel).filter_by(id=user_id))
            user = query.scalar()
            if user is not None:
                user.password = new_password
                return user.password
        return None

    async def delete_user(self, *, user_id: int):
        async with self._session.begin():
            query = await self._session.execute(select(UserModel).filter_by(id=user_id))
            user = query.scalar()
            if user is not None:
                await self._session.delete(user)
                await self._session.flush()  # 변경 사항을 일시적으로 세션에 반영
                await self._session.commit()  # 유저 삭제 후에 세션을 커밋
                return True  # 삭제 작업이 성공적으로 수행됨을 반환
        return False  # 삭제 작업 실패
    
    async def get_user_by_name(self, *, user_name: str):
        async with self._session.begin():
            query = select(UserModel).filter(UserModel.name == user_name)
            result = await self._session.execute(query)
            user = result.scalars().first()
            return user
    
    async def checked_today(self, *, user_id: int):
        async with self._session.begin():
            query = select(UserModel).filter(UserModel.id == user_id)
            result = await self._session.execute(query)
            user = result.scalars().first()
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="유저 정보가 없습니다.",
                )
            return user

    async def get_user_by_id(self, *, user_id: str):
        async with self._session.begin():
            query = select(UserModel).filter(UserModel.id == user_id)
            result = await self._session.execute(query)
            user = result.scalars().first()
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="유저 정보가 없습니다.",
                )
            return user
        
    async def update_user(self, user: UserModel) -> UserModel:
        try:
            self._session.add(user)
            await self._session.commit()
        except:
            await self._session.rollback()
            raise
        finally:
            await self._session.close()
        return user

    async def increment_purchase_count(self, user_id: int):
        async with self._session.begin():
            query = await self._session.execute(select(UserModel).filter_by(id=user_id))
            user = query.scalar()
            if user is not None:
                user.purchase_count += 1
                self._session.add(user)
                await self._session.commit()
                return user.purchase_count

    async def increment_sales_count(self, user_id: int):
        async with self._session.begin():
            query = await self._session.execute(select(UserModel).filter_by(id=user_id))
            user = query.scalar()
            if user is not None:
                user.sales_count += 1
                self._session.add(user)
                await self._session.commit()
                return user.sales_count
    
    async def decount_cash(self, user_id: int, decount:int):
        async with self._session.begin():
            query = await self._session.execute(select(UserModel).filter_by(id=user_id))
            user = query.scalar()
            if user is not None:
                user.cash -= decount
                self._session.add(user)
                await self._session.commit()
                return True

class ContentRepository:
    def __init__(self, session: AsyncSession):     #DB에 있는 세션을 변수에 저장 말그대로 init
        self._session = session
     
###
    async def create_content(self, *, content_tag:str, user_id: str, content_title: str, content_text: str, content_startprice: int, content_picture: str, bidder: str, price_info: str):
        async with self._session.begin():
            content_entity=ContentModel(
                userid=user_id,
                title=content_title,
                text= content_text,
                startprice=content_startprice,
                picture=content_picture,
                bidder=bidder,
                price_info=price_info,
                tag = content_tag
            )
            self._session.add(content_entity)
            await self._session.commit()
            return content_entity
        
    async def get_contents(self):
        async with self._session.begin():
            query = select(ContentModel)
            result = await self._session.execute(query)
            contents = result.scalars().all()

            if contents is None :
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="정보가 없습니다.",
                )
            return contents

    async def hot_contents(self):
        async with self._session.begin():
            query = (
                select(ContentModel)
                .order_by((ContentModel.recommend + ContentModel.view_count * 0.8).desc())
                .limit(7)
            )
            result = await self._session.execute(query)
            contents = result.scalars().all()

            if contents is None :
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="정보가 없습니다.",
                )
            return contents
        
    async def sales_contents(self, userid):
        async with self._session.begin():
            query = select(ContentModel).where(
            and_(ContentModel.userid == userid, ContentModel.state == "판매 완료")
        )
            result = await self._session.execute(query)
            contents = result.scalars().all()

            if contents is None :
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="정보가 없습니다.",
                )
            return contents
        
    async def buys_contents(self, userid):
        async with self._session.begin():
            
            query = select(ContentModel).where(
            and_(
                func.array_position(func.string_to_array(ContentModel.bidder, ','), userid) != None,
                ContentModel.state == "판매 완료"
            )
        )
            
            

            result = await self._session.execute(query)
            contents = result.scalars().all()

            if contents is None :
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="정보가 없습니다.",
                )
            return contents
    
    async def selling_contents(self, userid):
        async with self._session.begin():
            query = select(ContentModel).where(
            and_(ContentModel.userid == userid, ContentModel.state == "판매 중")
        )
            result = await self._session.execute(query)
            contents = result.scalars().all()

            if contents is None :
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="정보가 없습니다.",
                )
            return contents
        
    async def buying_contents(self, userid):
        async with self._session.begin():
            
            query = select(ContentModel).where(
            and_(
                func.array_position(func.string_to_array(ContentModel.bidder, ','), userid) != None,
                ContentModel.state == "판매 중"
            )
        )
            
            result = await self._session.execute(query)
            contents = result.scalars().all()

            if contents is None :
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="정보가 없습니다.",
                )
            return contents
        
    async def get_liked_contents(self, user_id):
        async with self._session.begin():
            query = select(ContentModel).join(LikeModel, ContentModel.id == LikeModel.content_id).filter(LikeModel.user_id == user_id)
            result = await self._session.execute(query)
            contents = result.scalars().all()
            return contents
    
    async def increase_view_count(self, content_id: int):
        async with self._session.begin():
            query = select(ContentModel).filter(ContentModel.id == content_id)
            content = await self._session.execute(query)
            content_entity = content.scalars().first()
            if content_entity is not None:
                content_entity.view_count += 1
                await self._session.commit()
                return True
            else:
                return False
        
    async def has_user_liked_content(self, user_id: str, content_id: int) -> bool:
        async with self._session.begin():
            query = select(LikeModel).filter(LikeModel.user_id == user_id, LikeModel.content_id == content_id)
            result = await self._session.execute(query)
            return result.scalars().first() is not None
        
    async def add_like(self, user_id: str, content_id: int):
        async with self._session.begin():
            like = LikeModel(user_id=user_id, content_id=content_id)
            self._session.add(like)
            await self._session.commit()

    async def remove_like(self, user_id: str, content_id: int):
        async with self._session.begin():
            query = select(LikeModel).filter(LikeModel.user_id == user_id, LikeModel.content_id == content_id)
            result = await self._session.execute(query)
            like = result.scalars().first()
            if like:
                await self._session.delete(like)
                await self._session.commit()

    async def increase_like_count(self, content_id: int):
        async with self._session.begin():
            query = select(ContentModel).filter(ContentModel.id == content_id)
            content = await self._session.execute(query)
            content_entity = content.scalars().first()
            if content_entity:
                content_entity.like_count += 1
                await self._session.commit()

    async def decrease_like_count(self, content_id: int):
        async with self._session.begin():
            query = select(ContentModel).filter(ContentModel.id == content_id)
            content = await self._session.execute(query)
            content_entity = content.scalars().first()
            if content_entity:
                content_entity.like_count -= 1
                await self._session.commit()

    async def finalize_auction(self, content_id: int, price:int, bidder:str, isBid:bool):
        async with self._session.begin():
            query = select(ContentModel).filter(ContentModel.id == content_id)
            result = await self._session.execute(query)
            content:ContentModel = result.scalars().first()
            if content:
                if isBid is True:            
                    content.state = "낙찰"
                    await self._session.commit()
                else:
                    content.state = "유찰"
                    await self._session.commit()
            else:
                return False


    async def get_content_by_title(self, title: str) -> ContentModel:
        async with self._session.begin():
            query = select(ContentModel).filter(ContentModel.title == title)
            result = await self._session.execute(query)
            content = result.scalars().first()
            return content
        
    async def update_content(self, content: ContentModel) -> ContentModel:
        async with self._session.begin_nested():  # 중첩된 트랜잭션 시작
            self._session.add(content)
            await self._session.commit()
            return content
    
    async def get_content_by_id(self, contents_id:int):
        async with self._session.begin_nested():
            query = select(ContentModel).filter(ContentModel.id == contents_id)
            result = await self._session.execute(query)
            content = result.scalars().first()
            await self._session.commit()
            return content
            
async def DaysCheck(user: UserModel):
    today = datetime.datetime.now()
    days = user.checked
    array = days.split(',')
    if user.month == today.month:
        if not(str(today.day) in array):
            if(user.checked ==""):
                user.checked = user.checked + str(today.day)
            else:
                user.checked = user.checked + "," + str(today.day)
                return False
        else:
            return True
    else:
        user.month = today.month
        user.checked = ""
        await DaysCheck(user)
