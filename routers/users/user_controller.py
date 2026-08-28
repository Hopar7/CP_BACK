from typing import List
import google_drive
import searchdb
import redis.asyncio as aioredis
import datetime, os, secrets, requests, json, secrets, string
from jose import JWTError
import jwt
from fastapi import APIRouter, Depends, File, HTTPException, Header, UploadFile, status, Form
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer
from dependencies.database import provide_session
from domains.users.repositories import ContentRepository, UserRepository
from dependencies.auth import Token, verify_password, create_access_token, hash_password, ALGORITHM
from dependencies.config import get_config
from domains.users.service import ContentService, UserService, verify_payment
from domains.users.dto import ContentResearchRequest, BidRequest, BidResponse, HistoryRequest, PaymentRequest, UserContentReponse, KakaoTalkRequset,UserItemGetResponse, UserLoginRequest, UserPostResponse, UserJoinRequest, UsercontentRequest, UserPassRequest,UserDeleteRequest, UserGetInfor, UsercontentRequest3,UsercontentRequest2,UsercontentLikeRequest,IncrementCountRequest
from domains.users.models import UserModel, ContentModel
from sqlalchemy.ext.asyncio import AsyncSession
conf_vars = get_config()
redis = aioredis.from_url(conf_vars.redis_url)
secret_key = conf_vars.jwt_secret_key
parent_folder_id = '1-1w_h8t3ICtJRC57iUuTG-Mwy5sUFXJQ'
name = "users"
router = APIRouter()
# OAuth2 토큰 스키마 생성
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR,'static/')
IMG_DIR = os.path.join(STATIC_DIR,'image/')
SERVER_IMG_DIR = os.path.join('https://port-0-cpbeck-hdoly2altu7slne.sel5.cloudtype.app/','=static/','image/')


@router.post(f"/{name}/check_duplicate")
async def check_duplicate(payload: UserItemGetResponse, db=Depends(provide_session)):
    user_service = UserService(user_repository=UserRepository(session=db))
    existing_user = await user_service.get_user_by_name(user_name=payload.data.name)
    if existing_user:
        return {"message": "사용 불가능한 사용자 아이디입니다."}

@router.post(f"/{name}/create")
async def create_user(payload: UserJoinRequest, db=Depends(provide_session)) -> str:
    print(payload)
    user_service = UserService(user_repository=UserRepository(session=db))
    user_name = await user_service.create_user(user_name=payload.data.name, user_pw=payload.data.password, user_nick = payload.data.nick_name)
    return user_name

@router.post(f"/{name}/tocheck")
async def attendance_check(payload: UserGetInfor, db=Depends(provide_session)):
    try:
        token_str = payload.data.authorization
        token = token_str.split("Bearer ")[0]  # Bearer 토큰에서 실제 토큰 값만 추출
        payload_data = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        user_id = payload_data.get("sub")  # 토큰에서 사용자 ID 추출
        user_service = UserService(user_repository=UserRepository(session=db))
        redata = await user_service.checked_today(user_id=user_id)
        return redata
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/kakaologin")
async def socialLogin(payload:KakaoTalkRequset, 
    db=Depends(provide_session),):
    url = "https://kauth.kakao.com/oauth/token"
    user_service = UserService(user_repository=UserRepository(session=db))
    data = {
        "grant_type": "authorization_code",
        "client_id": "369df2666853b0b05a21a4d65daa7261",
        "client_secret": "hIJsF8Cogy1TewavZxAuqd8RcDcqGSmv",
        "redirect_uri": "http://localhost:3000/KakaoRedirect",
        "code": payload.data.code
    }

    response = requests.post(url, data=data)
    tokens = response.json()

    if "access_token" in tokens:
        with open("kakao_token.json", "w") as fp:
            json.dump(tokens, fp)
            user_info = get_user_info(tokens.get("access_token"))
            if user_info:
                nickname = user_info['properties']['nickname']
                email = user_info['kakao_account']['email']
                user = await user_service.get_user_by_name(user_name=email)
                if user is not None:
                    access_token = create_access_token(data={"sub": user.id})
                    print(access_token)
                    return Token(token=access_token, type="bearer")
                else:
                    await user_service.create_user(user_name=email,user_nick=nickname,user_pw=generate_temp_password())
                    user = await user_service.get_user_by_name(user_name=email)
                    if user is not None:
                        access_token = create_access_token(data={"sub": user.id})
                        print(access_token)
                        return Token(token=access_token, type="bearer")
            else:
                print("Failed to get user information.")
    else:
        print(tokens)

# 로그인을 처리하는 엔드포인트
@router.post(f"/{name}/login")
async def login(
    payload: UserLoginRequest,
    db=Depends(provide_session),  # 데이터베이스 세션 제공을 위한 의존성 주입
) -> Token:
    user_name = payload.data.name
    user_password = payload.data.password
    # UserService와 UserRepository 생성
    user_service = UserService(user_repository=UserRepository(session=db))

    # 입력된 사용자 이름으로 사용자 정보 조회
    user = await user_service.get_user_by_name(user_name=user_name)

    # 입력된 비밀번호를 사용자 비밀번호와 비교하여 인증 확인
    if not verify_password(user_password, user.password):
        # 인증 실패 시 401 Unauthorized 에러 반환
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="비밀번호가 틀립니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )


    # 사용자 ID를 포함한 액세스 토큰 생성 및 반환
    access_token = create_access_token(data={"sub": user.id})
    print(access_token)
    return Token(token=access_token, type="bearer")

@router.post(f"/{name}/delete_user")
async def delete_user(payload: UserDeleteRequest, db=Depends(provide_session)):
    try:
        token_str = payload.data.authorization
        token = token_str.split("Bearer ")[0]  # Bearer 토큰에서 실제 토큰 값만 추출
        payload_data = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        user_id: int = payload_data.get("sub")  # 토큰에서 사용자 ID 추출

        user_service = UserService(user_repository=UserRepository(session=db))

        # 사용자 삭제
        delete_user_data = await user_service.delete_user(user_id=user_id)
        return delete_user_data
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

# 사용자 정보를 가져오는 엔드포인트
@router.post(f"/{name}/my_page")
async def get_item(
    payload: UserGetInfor,  # Authorization 헤더에서 토큰을 가져오기 위한 파라미터 추가
    db=Depends(provide_session),  # 데이터베이스 세션 제공을 위한 의존성 주입
):
    # UserService와 UserRepository 생성
    user_service = UserService(user_repository=UserRepository(session=db))

    # 토큰에서 Bearer를 제거하고 실제 토큰 값을 추출
    token = payload.data.authorization

    # 토큰을 디코딩하여 사용자 정보 추출
    payload_decode = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
    user_id_from_token: int = payload_decode.get("sub")
    # 주어진 user_id에 해당하는 사용자 정보 조회
    user = await user_service.get_user_by_id(user_id=user_id_from_token)

    # 조회된 사용자 정보를 UserItemGetResponse DTO 객체에 매핑하여 반환
    return user

@router.post(f"/{name}/changing_password")
async def change_password(payload: UserPassRequest, db=Depends(provide_session)):
    try:
        # 사용자 서비스 및 레포지토리 생성
        user_service = UserService(user_repository=UserRepository(session=db))
        # 토큰에서 사용자 ID 추출
        token = payload.data.authorization
        payload_decode = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        user_id: int = payload_decode.get("sub")
        
        print(user_id)
        # 현재 비밀번호 확인
        current_password = payload.data.user_password
        print(current_password)
        is_valid_current_pw = await user_service.check_current_password(user_id=user_id, current_pw=current_password)
        
        if not is_valid_current_pw:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="현재 비밀번호가 올바르지 않습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 새로운 비밀번호와 확인할 비밀번호를 가져옴
        new_password = payload.data.password
        confirmed_password = payload.data.confirm_password
        
        # 새로운 비밀번호와 확인할 비밀번호가 일치하는지 확인
        if new_password != confirmed_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="새로운 비밀번호와 확인 비밀번호가 일치하지 않습니다."
            )
        
        # 암호화된 새로운 비밀번호
        hashed_new_pw = hash_password(new_password)
        
        # 비밀번호 변경
        changed_pw = await user_service.change_password(user_id=user_id, new_pw=hashed_new_pw)
        if changed_pw == hashed_new_pw:
            return "비밀번호가 성공적으로 변경되었습니다."
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="비밀번호 변경에 실패했습니다."
            )
            
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
            
#컨텐츠 정보를 가져오는 엔드포인트
@router.get(f"/{name}/getcontents")
async def get_content(
    db=Depends(provide_session),  # 데이터베이스 세션 제공을 위한 의존성 주입
):
    # ContentService와 ContentRepository 생성
    content_service = ContentService(content_repository=ContentRepository(session=db))

    # 주어진 content_id에 해당하는 사용자 정보 조회
    content:ContentModel = await content_service.get_contents()

    # 조회된 컨텐츠 정보를 UserContentReponse DTO 객체에 매핑하여 반환
    return content

@router.get(f"/{name}/hotdeals_contents")
async def get_content(
    db=Depends(provide_session),
):
    content_service = ContentService(content_repository=ContentRepository(session=db))
    content:ContentModel = await content_service.hot_contents()
    return content

@router.get(f"/{name}/{{user_id}}")
async def get_item(
    user_id: int,
    authorization: str = Header(...),  # Authorization 헤더에서 토큰을 가져오기 위한 파라미터 추가
    db=Depends(provide_session),  # 데이터베이스 세션 제공을 위한 의존성 주입
) -> UserItemGetResponse:
    # 토큰에서 Bearer를 제거하고 실제 토큰 값을 추출
    token = authorization.split("Bearer ")[1]

    # 토큰을 디코딩하여 사용자 정보 추출
    payload_decode = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
    user_id_from_token: int = payload_decode.get("sub")

    # 사용자 ID가 토큰에서 추출된 사용자 ID와 일치하는지 확인
    if user_id != user_id_from_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다.",
        )

    # UserService와 UserRepository 생성
    user_service = UserService(user_repository=UserRepository(session=db))

    # 주어진 user_id에 해당하는 사용자 정보 조회
    user = user_service.get_user_by_id(user_id=user_id)

    # 조회된 사용자 정보를 UserItemGetResponse DTO 객체에 매핑하여 반환
    return UserItemGetResponse(
        data=UserItemGetResponse.DTO(
            id=user.id,  # 사용자 ID
            name=user.name,  # 사용자 이름
            nick_name=user.nick_name  #사용자 닉네임
        )
    )

@router.post("/writing")
async def writing(
    payload :UsercontentRequest, 
    db=Depends(provide_session)
):
    content_service = ContentService(content_repository=ContentRepository(session=db))
    user_service = UserService(user_repository=UserRepository(session=db))
    token = payload.data.authorization
    content_tag = google_drive.upload_file_to_drive(payload.data.picture, os.path.basename(payload.data.picture))
    payload_decode = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
    user_id: int = payload_decode.get("sub")
    user = await user_service.get_user_by_id(user_id=user_id)
    content= await content_service.create_content(
        user_id=user.name,
        content_title=payload.data.title,
        content_text=payload.data.text,
        content_startprice=payload.data.startprice,
        content_picture=os.path.basename(payload.data.picture),
        content_tag = content_tag
    )
    return True #리턴변수에 글 작성 성공?실패 리턴?

@router.post('/upload-images') #함수로 써야함 이미지받을때
async def upload_board(in_files: List[UploadFile] = File(...)):
      if not isinstance(in_files, list):
          return {"error": "in_files should be a list of UploadFile objects"}
    
      file_urls=[]
      for file in in_files:
          currentTime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
          saved_file_name = ''.join([currentTime, secrets.token_hex(16)])
          final_name = saved_file_name + ".jpg"
          file_location = os.path.join(IMG_DIR, final_name)
          with open(file_location, "wb+") as file_object:
              file_object.write(file.file.read())
          file_urls.append(SERVER_IMG_DIR + final_name)
    
      result = {'fileUrls': file_urls}
      file_name = IMG_DIR+final_name
      print(file_name)
      print(os.path.basename(file_name))
      return file_name


@router.get('/images/{file_name}')
async def get_image(file_name:str):
    return FileResponse(''.join([IMG_DIR,file_name]))

@router.post(f"/{name}/increase_view_count")
async def increase_view_count(payload: UsercontentRequest3, db=Depends(provide_session)):
    content_service = ContentService(content_repository=ContentRepository(session=db))
    redata = await content_service.increase_view_count(content_id=payload.data.content_id)
    return redata

@router.post('/search')
async def searchitem(
    payload : ContentResearchRequest,
    db=Depends(provide_session)
):
    content_service = ContentService(content_repository=ContentRepository(session=db))
    contents_list = await content_service.get_contents()
    
    
    searchsort= searchdb.searchtext(payload.data.search, contents_list)
    return searchsort

###
@router.post("/payments")
async def create_payment(
    payload: PaymentRequest,
    authorization: str = Header(...),
    db: AsyncSession = Depends(provide_session)
):
    user_service = UserService(user_repository=UserRepository(session=db))

    # 토큰에서 유저 정보 추출
    token_data = jwt.decode(authorization.split(" ")[1], secret_key, algorithms=[ALGORITHM])
    user_id = token_data.get("sub")

    user = await user_service.get_user_by_id(user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")

    if not await verify_payment(payload.data.imp_uid, payload.data.amount):
        raise HTTPException(status_code=400, detail="결제 검증 실패.")

    # 유저 캐쉬 업데이트
    updated_user = await user_service.update_user_cash(user=user, amount=payload.data.amount)

    return {
        "message": "결제가 성공적으로 처리되었습니다.",
        "data": payload,
        "updated_cash": updated_user.cash
    }

@router.post(f"/{name}/sales_history")
async def view_sales_history(
    payload: HistoryRequest,
    db=Depends(provide_session),
):
    content_service = ContentService(content_repository=ContentRepository(session=db))
    user_service = UserService(user_repository=UserRepository(session=db))
    token = payload.data.authorization
    payload_decode = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
    user_id: int = payload_decode.get("sub")
    user = await user_service.get_user_by_id(user_id=user_id)
    content:ContentModel = await content_service.sales_contents(userid=user.name)

    return content

@router.post(f"/{name}/buys_history")
async def view_buys_history(
    payload: HistoryRequest,
    db=Depends(provide_session),
):
    content_service = ContentService(content_repository=ContentRepository(session=db))
    user_service = UserService(user_repository=UserRepository(session=db))
    token = payload.data.authorization
    payload_decode = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
    user_id: int = payload_decode.get("sub")
    user = await user_service.get_user_by_id(user_id=user_id)
    content:ContentModel = await content_service.buys_contents(userid=user.name)

    return content

@router.post(f"/{name}/selling_contents")
async def view_sales_history(
    payload: HistoryRequest,
    db=Depends(provide_session),
):
    content_service = ContentService(content_repository=ContentRepository(session=db))
    user_service = UserService(user_repository=UserRepository(session=db))
    token = payload.data.authorization
    payload_decode = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
    user_id: int = payload_decode.get("sub")
    user = await user_service.get_user_by_id(user_id=user_id)
    content:ContentModel = await content_service.selling_contents(userid=user.name)

    return content

@router.post(f"/{name}/buying_contents")
async def view_buys_history(
    payload: HistoryRequest,
    db=Depends(provide_session),
):
    content_service = ContentService(content_repository=ContentRepository(session=db))
    user_service = UserService(user_repository=UserRepository(session=db))
    token = payload.data.authorization
    payload_decode = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
    user_id: int = payload_decode.get("sub")
    user = await user_service.get_user_by_id(user_id=user_id)
    content:ContentModel = await content_service.buying_contents(userid=user.name)

    return content


###


def get_user_info(access_token):
    url = "https://kapi.kakao.com/v2/user/me"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        user_info = response.json()
        return user_info
    else:
        return None
    
def generate_temp_password(length=10):
    """Generate a random temporary password."""
    characters = string.ascii_letters + string.digits
    temp_password = ''.join(secrets.choice(characters) for i in range(length))
    return temp_password

@router.post(f"/{name}/toggle_like")
async def toggle_like(payload: UsercontentLikeRequest, db=Depends(provide_session)):
    content_service = ContentService(content_repository=ContentRepository(session=db))
    user_service = UserService(user_repository=UserRepository(session=db))
    token_str = payload.data.authorization
    token = jwt.decode(token_str,secret_key, algorithms=[ALGORITHM])
    user_id = token.get("sub")
    print(user_id)
    user:UserModel = await user_service.get_user_by_id(user_id=user_id)
    print(user)
    await content_service.toggle_like(user_id=user.name, content_id=payload.data.content_id)
    return {"message": "좋아요 상태가 성공적으로 변경되었습니다."}  


@router.post("/users/increment_purchase_count")
async def increment_purchase_count(payload: IncrementCountRequest, db=Depends(provide_session)):
    user_service = UserService(user_repository=UserRepository(session=db))
    await user_service.increment_purchase_count(user_id=payload.data.user_id)
    return {"status": "success"}

@router.post("/users/increment_sales_count")
async def increment_sales_count(payload: IncrementCountRequest, db=Depends(provide_session)):
    user_service = UserService(user_repository=UserRepository(session=db))
    await user_service.increment_sales_count(user_id=payload.data.user_id)
    return {"status": "success"} 

@router.post(f"/{name}/liked_contents")
async def get_liked_contents(payload: UserGetInfor,db=Depends(provide_session)):
    content_service = ContentService(content_repository=ContentRepository(session=db))
    user_service = UserService(user_repository=UserRepository(session=db))
    token = payload.data.authorization
    payload_decode = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
    user_id = payload_decode.get("sub")
    user:UserModel = await user_service.get_user_by_id(user_id=user_id)
    liked_contents = await content_service.get_liked_contents(user_id=user.name)

    return liked_contents

@router.post(f"/{name}/is_liked")
async def is_content_liked(payload: UsercontentLikeRequest, db=Depends(provide_session)):
    content_service = ContentService(content_repository=ContentRepository(session=db))
    user_service = UserService(user_repository=UserRepository(session=db))

    token_str = payload.data.authorization
    token = jwt.decode(token_str, secret_key, algorithms=[ALGORITHM])
    user_id = token.get("sub")
    
    user = await user_service.get_user_by_id(user_id=user_id)
    
    is_liked = await content_service.has_user_liked_content(user_id=user.name, content_id=payload.data.content_id)
    
    return {"is_liked": is_liked}

@router.post("/finalize_auction")
async def finalize_auction(payload: UsercontentRequest3,db=Depends(provide_session)):
    content_service = ContentService(content_repository=ContentRepository(session=db))
    content:ContentModel = await content_service.get_content_by_id(contents_id=payload.data.content_id)
    bidder_list = content.bidder.split(",")
    price_list = content.price_info.split(",")
    isBid:bool
    if len(bidder_list) == 1:
        isBid = False
    else:
        isBid = True

    price = int(price_list[-1])
    bidder = bidder_list[-1]
    finalized_content = await content_service.finalize_auction(content_id=payload.data.content_id, price=price, bidder=bidder, isBid=isBid)
    return finalized_content

@router.post("/bid")
async def place_bid(
    payload: BidRequest,
    db: AsyncSession = Depends(provide_session)
) -> BidResponse:
    try:
        token = payload.data.authorization
        payload_decode = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        user_id: int = payload_decode.get("sub")

        user_service = UserService(user_repository=UserRepository(session=db))
        content_service = ContentService(content_repository=ContentRepository(session=db))

        user = await user_service.get_user_by_id(user_id=user_id)
        
        item = await content_service.get_content_by_title(title=payload.data.item_title)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        if payload.data.bid_amount <= item.startprice:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bid amount must be greater than current bid"
            )

        if payload.data.bid_amount > user.cash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient funds"
            )

        previous_bidder_names = item.bidder.split(",")
        previous_bidder_name = previous_bidder_names[-1]
        previous_price_info = item.price_info.split(",")
        previous_bid_amount = int(previous_price_info[-1])

        if previous_bidder_name != user.name:
            previous_bidder = await user_service.get_user_by_name(user_name=previous_bidder_name)
            await user_service.update_user_cash(user=previous_bidder, amount=previous_bid_amount)

        item.startprice = payload.data.bid_amount
        item.bidder = item.bidder+','+user.name
        item.price_info = item.price_info+','+str(payload.data.bid_amount)
        updated_item = await content_service.update_content(item)
        revalue = await user_service.decount_cash(user_id=user_id,decount=payload.data.bid_amount)
        return BidResponse(
            data=BidResponse.DTO(
                item_title=updated_item.title,
                new_bid_amount=updated_item.startprice,
                bidder=updated_item.bidder
            )
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )

@router.get("/price_data")
async def RePricedata(
    contents_id:int,
    db:AsyncSession = Depends(provide_session)
):
    contentservice = ContentService(content_repository=ContentRepository(session=db))
    content = await contentservice.get_contents(contents_id=contents_id)
    price_info = content.price_info.split(",")
    return price_info
