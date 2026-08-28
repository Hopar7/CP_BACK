from domains import Service
from dependencies.auth import hash_password, verify_password
from .repositories import ContentRepository, UserRepository
from .models import ContentModel, UserModel
import httpx

class UserService(Service):
    def __init__(self, *, user_repository: UserRepository):
        self._user_repository = user_repository

    async def update_user_cash(self, user: UserModel, amount: float) -> UserModel:
        user.cash += amount
        updated_user = await self._user_repository.update_user(user)
        return updated_user

    async def create_user(self, *, user_name: str, user_pw: str, user_nick: str) -> str:
        hashed_pw = hash_password(user_pw)
        user_name = await self._user_repository.create_user(user_name=user_name, password=hashed_pw, user_nick=user_nick)
        return user_name

    async def change_password(self, *, user_id, new_pw) -> str:
        check_changing = await self._user_repository.change_password(user_id=user_id, new_password=new_pw)
        return check_changing

    async def check_current_password(self, *, user_id, current_pw: str) -> bool:
        user_entity = await self._user_repository.get_user_by_id(user_id=user_id)
        print(current_pw)
        print(user_entity.password)
        if verify_password(current_pw, user_entity.password):
            return True
        else:
            return False
    
    async def delete_user(self, *, user_id):
        delete_user_result = await self._user_repository.delete_user(user_id=user_id)
        return delete_user_result
    
    # 사용자 이름으로 사용자 정보를 가져오는 메서드
    async def get_user_by_name(self, *, user_name: str) -> UserModel:
        user_entity = await self._user_repository.get_user_by_name(user_name=user_name)
        return user_entity
    
    async def get_user_by_id(self, *, user_id: int):
        user_entity = await self._user_repository.get_user_by_id(user_id=user_id)
        return user_entity
    
    async def checked_today(self, *, user_id: int):
        await self._user_repository.checked_today(user_id=user_id)

    async def increment_purchase_count(self, user_id: int) -> int:
        purchase_count = await self._user_repository.increment_purchase_count(user_id=user_id)
        return purchase_count

    async def increment_sales_count(self, user_id: int) -> int:
        sales_count = await self._user_repository.increment_sales_count(user_id=user_id)
        return sales_count
    
    async def decount_cash(self, user_id:int, decount:int):
        revalue = await self._user_repository.decount_cash(user_id=user_id,decount=decount)
        return revalue
    
class ContentService(Service):
    def __init__(self, *, content_repository: ContentRepository):
        self._content_repository = content_repository

    async def create_content(self, *, content_tag, user_id: str, content_title: str, content_text: str, content_startprice: int, content_picture: str) -> int:
        content_entity = await self._content_repository.create_content(
            user_id=user_id,
            content_title=content_title,
            content_text=content_text,
            content_startprice=content_startprice,
            content_picture=content_picture,
            bidder=user_id,
            price_info=str(content_startprice),
            content_tag = content_tag
        )
        return content_entity

    async def get_contents(self) -> ContentModel:
        content_entity = await self._content_repository.get_contents()
        return content_entity
    
    async def hot_contents(self) -> ContentModel:
        content_entity = await self._content_repository.hot_contents()
        return content_entity
    
    async def sales_contents(self, userid) -> ContentModel:
        content_entity = await self._content_repository.sales_contents(userid=userid)
        return content_entity
    
    async def buys_contents(self, userid) -> ContentModel:
        content_entity = await self._content_repository.buys_contents(userid=userid)
        return content_entity
    
    async def selling_contents(self, userid) -> ContentModel:
        content_entity = await self._content_repository.selling_contents(userid=userid)
        return content_entity
    
    async def buying_contents(self, userid) -> ContentModel:
        content_entity = await self._content_repository.buying_contents(userid=userid)
        return content_entity

    async def increase_view_count(self, content_id: int):
        redata = await self._content_repository.increase_view_count(content_id=content_id)
        return redata

    async def toggle_like(self, user_id: str, content_id: int):
        has_liked = await self._content_repository.has_user_liked_content(user_id, content_id)
        if has_liked:
            await self._content_repository.remove_like(user_id, content_id)
            await self._content_repository.decrease_like_count(content_id)
        else:
            await self._content_repository.add_like(user_id, content_id)
            await self._content_repository.increase_like_count(content_id)

    async def get_liked_contents(self, user_id: str):
        contents = await self._content_repository.get_liked_contents(user_id)
        return contents

    async def finalize_auction(self, content_id: int, bidder:str, price:int, isBid:bool):
        finalized_content = await self._content_repository.finalize_auction(content_id=content_id,price=price,bidder=bidder, isBid=isBid)
        return finalized_content
    
    async def get_content_by_title(self, title: str) -> ContentModel:
        content_entity = await self._content_repository.get_content_by_title(title=title)
        return content_entity
    
    async def update_content(self, content: ContentModel) -> ContentModel:
        updated_content = await self._content_repository.update_content(content)
        return updated_content
    
    async def get_content_by_id(self, contents_id:int):
        content = await self._content_repository.get_content_by_id(contents_id=contents_id)
        return content
    
    async def has_user_liked_content(self, user_id: str, content_id: int) -> bool:
        return await self._content_repository.has_user_liked_content(user_id=user_id, content_id=content_id)


async def verify_payment(imp_uid: str, amount: float) -> bool:
    token = await get_token()
    headers = {"Authorization": token}
    url = f"https://api.iamport.kr/payments/{imp_uid}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
    payment_data = response.json().get("response", {})

    return payment_data.get("amount") == amount

async def get_token() -> str:
    url = "https://api.iamport.kr/users/getToken"
    payload = {
        "imp_key": "2162528360828512",  # 아임포트에서 발급받은 키
        "imp_secret": "F6tol6jfoHNWyUA28j98apIQvGjbEGQQwpBS0d7A76dJekALGmUoIgHhPF69sSQ7wbG77E8e1MVBQz69"  # 아임포트에서 발급받은 시크릿
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
    token_data = response.json().get("response", {})
    return token_data.get("access_token")
