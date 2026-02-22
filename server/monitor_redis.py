"""
Redis Token Monitor - View refresh token statistics
"""
import redis
from datetime import datetime


def monitor_tokens():
    """Monitor refresh tokens in Redis"""
    try:
        client = redis.from_url(
            "redis://localhost:6379/0",
            encoding="utf-8",
            decode_responses=True
        )
        
        print("=" * 60)
        print("🔍 REDIS TOKEN MONITOR")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Get all refresh token keys
        token_keys = list(client.scan_iter(match="refresh_token:*"))
        
        print(f"📊 Total Refresh Tokens: {len(token_keys)}")
        
        if len(token_keys) > 0:
            # Count by user
            user_tokens = {}
            revoked_count = 0
            
            print("\n📝 Token Details:")
            print("-" * 60)
            
            for i, key in enumerate(token_keys[:10], 1):  # Show first 10
                data = client.hgetall(key)
                user_id = data.get("user_id", "unknown")
                revoked = data.get("revoked") == "1"
                ttl = client.ttl(key)
                
                # Count by user
                user_tokens[user_id] = user_tokens.get(user_id, 0) + 1
                if revoked:
                    revoked_count += 1
                
                status = "🔴 REVOKED" if revoked else "🟢 ACTIVE"
                ttl_str = f"{ttl // 3600}h {(ttl % 3600) // 60}m" if ttl > 0 else "EXPIRED"
                
                print(f"{i}. Token ID: {key.split(':')[1][:16]}...")
                print(f"   User: {user_id[:16]}...")
                print(f"   Status: {status}")
                print(f"   TTL: {ttl_str}")
                print()
            
            if len(token_keys) > 10:
                print(f"... and {len(token_keys) - 10} more tokens\n")
            
            print("-" * 60)
            print(f"\n📈 Statistics:")
            print(f"   Active tokens: {len(token_keys) - revoked_count}")
            print(f"   Revoked tokens: {revoked_count}")
            print(f"   Unique users: {len(user_tokens)}")
            print(f"   Avg tokens/user: {len(token_keys) / len(user_tokens):.1f}")
            
            # Highlight users with multiple tokens
            multi_token_users = {uid: count for uid, count in user_tokens.items() if count > 1}
            if multi_token_users:
                print(f"\n⚠️  Users with multiple tokens: {len(multi_token_users)}")
                for uid, count in sorted(multi_token_users.items(), key=lambda x: x[1], reverse=True)[:5]:
                    print(f"      • {uid[:16]}... has {count} tokens")
                print(f"\n   💡 Tip: Run 'python cleanup_duplicate_tokens.py' to clean up duplicates")
            
        else:
            print("\n✨ No tokens in Redis yet")
        
        # Memory info
        memory_info = client.info("memory")
        used_memory_mb = int(memory_info['used_memory']) / (1024 * 1024)
        
        print(f"\n💾 Redis Memory:")
        print(f"   Used: {used_memory_mb:.2f} MB")
        
        # Get all keys count
        all_keys = client.dbsize()
        print(f"\n🔑 Total Redis Keys: {all_keys}")
        
        print("\n" + "=" * 60)
        
        client.close()
        
    except redis.ConnectionError:
        print("❌ Cannot connect to Redis on localhost:6379")
    except Exception as e:
        print(f"❌ Error: {e}")


def clear_all_tokens():
    """Clear all refresh tokens (use with caution!)"""
    try:
        client = redis.from_url("redis://localhost:6379/0")
        
        token_keys = list(client.scan_iter(match="refresh_token:*"))
        
        if len(token_keys) > 0:
            confirm = input(f"\n⚠️  Delete {len(token_keys)} tokens? (yes/no): ")
            if confirm.lower() == "yes":
                for key in token_keys:
                    client.delete(key)
                print(f"✅ Deleted {len(token_keys)} tokens")
            else:
                print("❌ Cancelled")
        else:
            print("✨ No tokens to delete")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        clear_all_tokens()
    else:
        monitor_tokens()
        print("\n💡 Tip: Run 'python monitor_redis.py --clear' to delete all tokens")
