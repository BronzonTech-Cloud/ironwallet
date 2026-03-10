import os

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer

from shared.config import settings
from shared.logging_utils import get_logger
from shared.security import decode_access_token

logger = get_logger("api-gateway")

app = FastAPI()

AUTH_URL = os.getenv("AUTH_SERVICE_URL")
WALLET_URL = os.getenv("WALLET_SERVICE_URL")
TXN_URL = os.getenv("TRANSACTION_SERVICE_URL")
ADMIN_URL = os.getenv("ADMIN_SERVICE_URL")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload


async def proxy_request(
    url: str, method: str, content: bytes, headers: dict, params: dict
):
    async with httpx.AsyncClient() as client:
        # Forward headers but remove host/len to let httpx handle it
        forward_headers = {
            k: v
            for k, v in headers.items()
            if k.lower() not in ["host", "content-length"]
        }
        try:
            resp = await client.request(
                method, url, content=content, headers=forward_headers, params=params
            )
            return resp.json(), resp.status_code
        except Exception as e:
            logger.error(f"Proxy error: {e}")
            raise HTTPException(status_code=500, detail="Service unavailable")


@app.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def auth_proxy(path: str, request: Request):
    body = await request.body()
    resp, status = await proxy_request(
        f"{AUTH_URL}/auth/{path}",
        request.method,
        body,
        request.headers,
        request.query_params,
    )
    if status >= 400:
        raise HTTPException(status_code=status, detail=resp)
    return resp


@app.api_route("/wallet/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def wallet_proxy(path: str, request: Request, user=Depends(get_current_user)):
    body = await request.body()
    resp, status = await proxy_request(
        f"{WALLET_URL}/wallet/{path}",
        request.method,
        body,
        request.headers,
        request.query_params,
    )
    if status >= 400:
        raise HTTPException(status_code=status, detail=resp)
    return resp


@app.api_route("/transaction/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def transaction_proxy(
    path: str, request: Request, user=Depends(get_current_user)
):
    body = await request.body()
    resp, status = await proxy_request(
        f"{TXN_URL}/transaction/{path}",
        request.method,
        body,
        request.headers,
        request.query_params,
    )
    if status >= 400:
        raise HTTPException(status_code=status, detail=resp)
    return resp


@app.api_route("/admin/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def admin_proxy(path: str, request: Request, user=Depends(get_current_user)):
    body = await request.body()
    resp, status = await proxy_request(
        f"{ADMIN_URL}/admin/{path}",
        request.method,
        body,
        request.headers,
        request.query_params,
    )
    if status >= 400:
        raise HTTPException(status_code=status, detail=resp)
    return resp
