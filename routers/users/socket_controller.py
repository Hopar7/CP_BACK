from typing import List
import redis.asyncio as aioredis
from fastapi import APIRouter, FastAPI, WebSocket, WebSocketDisconnect, Depends
from dependencies.auth import Token, verify_password, create_access_token, hash_password, ALGORITHM
from dependencies.config import get_config
from domains.users.dto import SocketGroupDTO

conf_vars = get_config()
redis = aioredis.from_url(conf_vars.redis_url)
secret_key = conf_vars.jwt_secret_key
parent_folder_id = '1-1w_h8t3ICtJRC57iUuTG-Mwy5sUFXJQ'
name = "socket"
router = APIRouter()

# WebSocket client and group management dictionaries
websocket_clients = {}
websocket_group = {"자유 게시판": []}  # Initialize with "자유 게시판" group

@router.post("/createGroup")
async def create_group(payload: SocketGroupDTO):
    if payload.data.groupname not in websocket_group:
        websocket_group[payload.data.groupname] = []
    websocket_group[payload.data.groupname].append(payload.data.username)
    return {"groupname": payload.data.groupname}

@router.post("/joinGroup")
async def join_group(payload: SocketGroupDTO):
    if payload.groupname in websocket_group:
        websocket_group[payload.data.groupname].append(payload.data.username)
    else:
        websocket_group[payload.data.groupname] = [payload.data.username]
    return {"groupname": payload.data.groupname}

@router.websocket("/ws/{username}/{groupname}")
async def websocket_endpoint(websocket: WebSocket, username: str, groupname: str):
    await websocket.accept()
    print(f"Client connected: {username}")

    if groupname not in websocket_group:
        websocket_group[groupname] = []
    websocket_group[groupname].append(username)

    websocket_clients[username] = websocket

    try:
        await websocket.send_text(f"Welcome to the group {groupname}, {username}")
        while True:
            data = await websocket.receive_text()
            print(f"Message received: {data} from {username}")

            # Send the message to other users in the same group
            for member in websocket_group[groupname]:
                if member != username and member in websocket_clients:
                    await websocket_clients[member].send_text(f"{username}: {data}")
    except WebSocketDisconnect:
        print(f"Connection closed for {username}")
    except Exception as e:
        print(f"Exception for {username}: {e}")
    finally:
        # Remove client from the group and clients dictionary on disconnect
        websocket_group[groupname].remove(username)
        if not websocket_group[groupname]:  # Clean up if the group is empty
            del websocket_group[groupname]
        del websocket_clients[username]
        print(f"Client {username} disconnected")

app = FastAPI()

app.include_router(router)
