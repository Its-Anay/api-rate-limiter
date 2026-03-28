from fastapi import Request, HTTPException
from app.database import get_valkey

def rate_limit(strategy, limit: int, window: int):
    async def dependency(request: Request):
        ip = request.client.host
        key = f"rate_limit:{request.url.path}:{ip}"
        
        async with get_valkey() as redis:
            allowed = await strategy.should_allow(redis, key, limit, window)
        
        if not allowed:
            raise HTTPException(status_code=429, detail="Too Many Requests")
    
    return dependency