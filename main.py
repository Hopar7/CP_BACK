from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles
import logging
import traceback

from dependencies.database import init_db
from dependencies.config import get_config

from routers import router as main_router

app = FastAPI(
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)
#ㅎㅇㅎㅇ
# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 라우터 추가
app.include_router(main_router)

# 데이터베이스 초기화
init_db(config=get_config())

# 예외 처리
@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    logging.error(traceback.format_exc())
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
