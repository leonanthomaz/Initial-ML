# src/middlewares/block_local_scans.py

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config.settings import Configuration

class BlockLocalScansMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.config = Configuration()

    async def dispatch(self, request: Request, call_next):
        if self.config.environment == "development":
            ip = request.client.host

            if ip.startswith("192.168."):
                return Response(status_code=403)

        return await call_next(request)

