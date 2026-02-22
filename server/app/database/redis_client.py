import redis
from typing import Optional
from app.config import settings


class RedisClient:
    """Redis client for caching and token storage"""
    
    def __init__(self):
        self.client = None
    
    def connect(self):
        """Initialize Redis connection"""
        try:
            self.client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
                health_check_interval=30
            )
            # Test connection
            self.client.ping()
            print("✅ Redis connected successfully")
        except redis.ConnectionError as e:
            print(f"❌ Redis connection failed: {e}")
            print("⚠️  Falling back to database for token storage")
            self.client = None
        except Exception as e:
            print(f"❌ Redis error: {e}")
            self.client = None
    
    def disconnect(self):
        """Close Redis connection"""
        if self.client:
            self.client.close()
            print("Redis connection closed")
    
    def is_available(self) -> bool:
        """Check if Redis is available"""
        if not self.client:
            return False
        try:
            return self.client.ping()
        except:
            return False
    
    # ========== Refresh Token Operations ==========
    
    def store_refresh_token(self, token_id: str, user_id: str, token_hash: str, ttl_seconds: int) -> bool:
        """
        Store refresh token in Redis with automatic expiration
        Key format: refresh_token:{token_id}
        """
        if not self.is_available():
            return False
        
        try:
            key = f"refresh_token:{token_id}"
            data = {
                "user_id": user_id,
                "token_hash": token_hash,
                "revoked": "0"
            }
            # Use HSET for storing hash data and EXPIRE for TTL
            self.client.hset(key, mapping=data)
            self.client.expire(key, ttl_seconds)
            return True
        except Exception as e:
            print(f"Redis store error: {e}")
            return False
    
    def get_refresh_token(self, token_id: str) -> Optional[dict]:
        """Get refresh token data from Redis"""
        if not self.is_available():
            return None
        
        try:
            key = f"refresh_token:{token_id}"
            data = self.client.hgetall(key)
            if not data:
                return None
            return {
                "user_id": data.get("user_id"),
                "token_hash": data.get("token_hash"),
                "revoked": data.get("revoked") == "1"
            }
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
    
    def revoke_refresh_token(self, token_id: str) -> bool:
        """Mark a refresh token as revoked"""
        if not self.is_available():
            return False
        
        try:
            key = f"refresh_token:{token_id}"
            self.client.hset(key, "revoked", "1")
            return True
        except Exception as e:
            print(f"Redis revoke error: {e}")
            return False
    
    def delete_refresh_token(self, token_id: str) -> bool:
        """Delete a refresh token from Redis"""
        if not self.is_available():
            return False
        
        try:
            key = f"refresh_token:{token_id}"
            self.client.delete(key)
            return True
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False
    
    def get_token_ttl(self, token_id: str) -> Optional[int]:
        """Get TTL (time to live) of a refresh token in seconds"""
        if not self.is_available():
            return None
        
        try:
            key = f"refresh_token:{token_id}"
            ttl = self.client.ttl(key)
            return ttl if ttl > 0 else None
        except Exception as e:
            print(f"Redis TTL error: {e}")
            return None
    
    def cleanup_expired_user_tokens(self, user_id: str) -> int:
        """
        Clean up expired or old tokens for a user
        Keeps only the most recent tokens (up to 3)
        """
        if not self.is_available():
            return 0
        
        try:
            pattern = "refresh_token:*"
            user_tokens = []
            
            # Find all tokens for this user with their TTL
            for key in self.client.scan_iter(match=pattern):
                data = self.client.hgetall(key)
                if data.get("user_id") == user_id and data.get("revoked") != "1":
                    ttl = self.client.ttl(key)
                    user_tokens.append((key, ttl))
            
            # If user has more than 3 active tokens, remove the oldest ones
            if len(user_tokens) > 3:
                # Sort by TTL (ascending) - tokens with less TTL are older/expiring sooner
                user_tokens.sort(key=lambda x: x[1])
                # Keep the 3 newest tokens (highest TTL), delete the rest
                tokens_to_delete = user_tokens[:-3]
                
                count = 0
                for key, _ in tokens_to_delete:
                    self.client.delete(key)
                    count += 1
                
                return count
            
            return 0
        except Exception as e:
            print(f"Redis cleanup error: {e}")
            return 0
    
    def revoke_all_user_tokens(self, user_id: str) -> int:
        """
        Revoke all refresh tokens for a user (logout from all devices)
        Returns number of tokens revoked
        """
        if not self.is_available():
            return 0
        
        try:
            # Find all refresh tokens for this user
            pattern = "refresh_token:*"
            count = 0
            
            for key in self.client.scan_iter(match=pattern):
                data = self.client.hgetall(key)
                if data.get("user_id") == user_id:
                    self.client.hset(key, "revoked", "1")
                    count += 1
            
            return count
        except Exception as e:
            print(f"Redis revoke all error: {e}")
            return 0
    
    def delete_all_user_tokens(self, user_id: str) -> int:
        """
        Delete all refresh tokens for a user
        Returns number of tokens deleted
        """
        if not self.is_available():
            return 0
        
        try:
            pattern = "refresh_token:*"
            count = 0
            
            for key in self.client.scan_iter(match=pattern):
                data = self.client.hgetall(key)
                if data.get("user_id") == user_id:
                    self.client.delete(key)
                    count += 1
            
            return count
        except Exception as e:
            print(f"Redis delete all error: {e}")
            return 0
    
    # ========== Access Token Blacklist (for logout before expiry) ==========
    
    def blacklist_access_token(self, token_jti: str, ttl_seconds: int) -> bool:
        """
        Add access token to blacklist (for logout)
        TTL should match token expiry
        """
        if not self.is_available():
            return False
        
        try:
            key = f"blacklist:{token_jti}"
            self.client.setex(key, ttl_seconds, "1")
            return True
        except Exception as e:
            print(f"Redis blacklist error: {e}")
            return False
    
    def is_token_blacklisted(self, token_jti: str) -> bool:
        """Check if access token is blacklisted"""
        if not self.is_available():
            return False
        
        try:
            key = f"blacklist:{token_jti}"
            return self.client.exists(key) > 0
        except Exception as e:
            print(f"Redis blacklist check error: {e}")
            return False
    
    # ========== Rate Limiting (alternative to fastapi-limiter) ==========
    
    def increment_rate_limit(self, key: str, window_seconds: int) -> int:
        """
        Increment rate limit counter
        Returns current count
        """
        if not self.is_available():
            return 0
        
        try:
            rate_key = f"rate_limit:{key}"
            count = self.client.incr(rate_key)
            if count == 1:
                self.client.expire(rate_key, window_seconds)
            return count
        except Exception as e:
            print(f"Redis rate limit error: {e}")
            return 0


# Global Redis client instance
redis_client = RedisClient()


def get_redis() -> RedisClient:
    """Dependency to get Redis client"""
    return redis_client
