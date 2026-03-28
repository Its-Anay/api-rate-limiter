from fastapi import FastAPI,Depends
from app.middleware import RateLimitMiddleware
from app.strategies.fixed_window import FixedWindowStrategy
from app.strategies.sliding_window import SlidingWindowStrategy
from app.strategies.leaky_bucket import LeakyBucketStrategy
from app.strategies.token_bucket import TokenBucketStrategy
from app.dependencies import rate_limit

app = FastAPI()

app.add_middleware(
    RateLimitMiddleware,
    strategy= SlidingWindowStrategy(),
    limit=5,
    window=60
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/fixedwindow", dependencies=[Depends(rate_limit(limit=10, window=60, strategy=FixedWindowStrategy()))])
async def ping():
    return {"message": "DONT OVERUSE i have fixed window algo"}

@app.get("/slidingwindow", dependencies=[Depends(rate_limit(limit=10, window=60, strategy=SlidingWindowStrategy()))])
async def ping():
    return {"message": "DONT OVERUSE i have sliding window algo"}

@app.get("/leakybucket", dependencies=[Depends(rate_limit(limit=10, window=60, strategy=LeakyBucketStrategy()))])
async def ping():
    return {"message": "DONT OVERUSE i have leaky bucket algo"}

@app.get("/tokenbucket", dependencies=[Depends(rate_limit(limit=10, window=60, strategy=TokenBucketStrategy()))])
async def ping():
    return {"message": "DONT OVERUSE i have token bucket algo"}