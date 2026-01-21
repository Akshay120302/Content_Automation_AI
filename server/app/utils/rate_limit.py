from fastapi_limiter.depends import RateLimiter

# Signup: 5 attempts per hour per IP
signup_rate_limit = RateLimiter(
    times=5,
    seconds=60 * 60
)

# Login: 5 attempts per 15 minutes per IP
login_rate_limit = RateLimiter(
    times=5,
    seconds=15 * 60
)

# Refresh token: optional, defensive
refresh_rate_limit = RateLimiter(
    times=10,
    seconds=10 * 60
)
