# File: rate_limiter.py
from upstash_redis import Redis
from datetime import datetime
from config import UPSTASH_REDIS_REST_URL, UPSTASH_REDIS_REST_TOKEN, DAILY_GUEST_LIMIT

redis_client = None
if UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN:
    try:
        redis_client = Redis(url=UPSTASH_REDIS_REST_URL, token=UPSTASH_REDIS_REST_TOKEN)
        print("✅ Upstash Redis client configured.")
    except Exception as e:
        print(f"❌ Could not configure Upstash Redis client. Guest tier will be disabled. Error: {e}")
        redis_client = None
else:
    print("⚠️ Upstash Redis credentials not found. Guest tier will be disabled.")

def get_today_key():
    """Returns a Redis key unique for the current day."""
    return f"api_usage:{datetime.utcnow().strftime('%Y-%m-%d')}"

def check_and_increment_usage():
    """Checks and increments guest usage against the daily limit in Redis."""
    if not redis_client:
        return False
        
    today_key = get_today_key()
    
    current_usage = redis_client.get(today_key)
    usage_count = int(current_usage) if current_usage else 0
    
    if usage_count >= DAILY_GUEST_LIMIT:
        print(f"🚨 Daily guest limit of {DAILY_GUEST_LIMIT} reached.")
        return False
    
    # --- THIS IS THE CORRECTED LOGIC ---
    # We execute the commands directly, which is simpler and avoids the pipeline error.
    # The performance difference for two commands is negligible.
    new_count = redis_client.incr(today_key)
    
    # Set the expiration only once when the key is first created for the day
    if new_count == 1:
        redis_client.expire(today_key, 90000) # 25 hours
    
    print(f"✅ Guest usage count is now {new_count}/{DAILY_GUEST_LIMIT}.")
    return True