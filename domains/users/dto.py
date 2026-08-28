from pydantic import BaseModel
from fastapi import Header,Query,UploadFile

class UserItemGetResponse(BaseModel): # 사용자 정보를 가져오는 응답에 대한 데이터 모델을 정의
    class DTO(BaseModel):
        id: int
        name: str
        nick_name: str
    data: DTO

class UserGetInfor(BaseModel):
    class DTO(BaseModel):
        authorization: str = Header(...)
    data:DTO

class UserLoginRequest(BaseModel):
    class DTO(BaseModel):
        name: str
        password: str
    data: DTO

class UserJoinRequest(BaseModel):
    class DTO(BaseModel):
        name: str
        password: str
        nick_name: str
    data: DTO

class UserPostResponse(BaseModel): # 사용자 정보를 가져오는 응답에 대한 데이터 모델을 정의
    class DTO(BaseModel):
        name: str
        password: str
    data: DTO


    
class UsercontentRequest(BaseModel):
    class DTO(BaseModel):
        authorization:str= Header(...) #글작성 아이디
        title:str        #글 제목
        text:str     #글 내용
        startprice:int   #시작 가격
        picture:str    #물품 사진
    data:DTO

class UserPassRequest(BaseModel):
    class DTO(BaseModel):
        user_password: str
        password: str
        confirm_password: str
        authorization: str = Header(...)
    data:DTO

class UserDeleteRequest(BaseModel):
    class DTO(BaseModel):
        authorization: str = Header(...)
    data:DTO

class UserContentReponse(BaseModel):
    class DTO(BaseModel):
        title:str
        text:str
        startprice:int
    data:DTO

class UsercontentRequest2(BaseModel):
    class DTO(BaseModel):
        userid:str         #글작성 아이디
        title:str        #글 제목
        text:str     #글 내용
        startprice:int   #시작 가격
    data:DTO

class KakaoTalkRequset(BaseModel):
    class DTO(BaseModel):
        code:str         #글작성 아이디
    data:DTO

class UsercontentRequest3(BaseModel):
    class DTO(BaseModel):
        content_id: int
    data:DTO

class ContentResearchRequest(BaseModel):
    class DTO(BaseModel):
        search : str
    data:DTO

class PaymentRequest(BaseModel):
    class Data(BaseModel):
        imp_uid: str
        amount: float
        method: str

    data: Data

class UsercontentLikeRequest(BaseModel):
    class DTO(BaseModel):
        authorization:str= Header(...)
        content_id: int
    data: DTO

class IncrementCountRequest(BaseModel):
    class DTO(BaseModel):
        authorization:str= Header(...)
        content_id: int
    data: DTO

class HistoryRequest(BaseModel):
    class DTO(BaseModel):
        authorization:str= Header(...)
    data: DTO

class BidRequest(BaseModel):
    class DTO(BaseModel):
        authorization: str = Header(...)
        item_title: str
        bid_amount: int
    data: DTO

class BidResponse(BaseModel):
    class DTO(BaseModel):
        item_title: str
        new_bid_amount: int
        bidder: str
    data: DTO

class SocketGroupDTO(BaseModel):
    class DTO(BaseModel):
        username: str
        groupname: str
    data:DTO