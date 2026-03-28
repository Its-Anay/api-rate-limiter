# Rate Limiter

A FastAPI service that demonstrates four rate limiting algorithms backed by [Valkey](https://valkey.io/) (Redis-compatible). Rate limiting can be applied globally via middleware or per-route via dependency injection.

## Algorithms

| Algorithm | How it works |
|---|---|
| **Fixed Window** | Counts requests in a fixed time window. Resets hard at the end of each window. |
| **Sliding Window** | Uses a sorted set of timestamps; counts only requests within the last `window` seconds. No hard reset, so it handles burst traffic at window boundaries better than fixed window. |
| **Token Bucket** | Bucket starts full (`limit` tokens). Each request consumes one token. Tokens refill at a constant rate. Allows short bursts up to bucket capacity. |
| **Leaky Bucket** | Requests enter a queue that drains at a fixed rate. Smooths out bursts — excess requests beyond queue capacity are dropped. |

All algorithms are implemented as atomic Lua scripts executed on Valkey, so they are race-condition safe.

## Project Structure

```
.
├── app/
│   ├── main.py              # FastAPI app, routes, middleware setup
│   ├── database.py          # Valkey async connection (context manager)
│   ├── middleware.py        # Global rate limit middleware (applies to all routes)
│   ├── dependencies.py      # Per-route rate limit dependency
│   └── strategies/
│       ├── base.py          # Abstract base class for strategies
│       ├── fixed_window.py
│       ├── sliding_window.py
│       ├── token_bucket.py
│       └── leaky_bucket.py
├── tests/
│   └── test_rate_limiter.py
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Two Ways to Apply Rate Limiting

### 1. Middleware (global)

Applied to **every** route. Configured in `main.py`:

```python
app.add_middleware(
    RateLimitMiddleware,
    strategy=SlidingWindowStrategy(),
    limit=5,
    window=60
)
```

Returns `HTTP 429 Too Many Requests` when the limit is exceeded.

### 2. Per-route Dependency

Applied to specific routes only. Each route can use a different algorithm:

```python
@app.get("/tokenbucket", dependencies=[Depends(rate_limit(limit=10, window=60, strategy=TokenBucketStrategy()))])
async def handler():
    ...
```

Rate limit keys are scoped per route + IP (`rate_limit:<path>:<ip>`), so limits on one route don't affect others.

## Routes

| Route | Algorithm | Limit |
|---|---|---|
| `GET /` | Sliding Window (middleware) | 5 req / 60s |
| `GET /fixedwindow` | Fixed Window | 10 req / 60s |
| `GET /slidingwindow` | Sliding Window | 10 req / 60s |
| `GET /leakybucket` | Leaky Bucket | 10 req / 60s |
| `GET /tokenbucket` | Token Bucket | 10 req / 60s |

## Running

### With Docker Compose (recommended)

```bash
docker compose up --build
```

The app starts at `http://localhost:8000`. Valkey runs on port `6379`.

### Locally

Requires a running Valkey/Redis instance on `localhost:6379`.

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Set `VALKEY_URL` to point to a different instance:

```bash
VALKEY_URL=redis://myhost:6379 uvicorn app.main:app --reload
```

## Testing

Tests require a running Valkey instance on `localhost:6379`.

```bash
pytest tests/
```

The test suite covers the global middleware (sliding window):
- First 5 requests return `200`
- 6th request returns `429`
- Requests succeed again after the window resets

## What Is Not Implemented Yet

- Rate limit response headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`)
- Per-user / API key based rate limiting (currently only IP-based)
- Tests for per-route dependency and individual strategy routes
- Configuring rate limits via environment variables
