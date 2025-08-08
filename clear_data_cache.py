#!/usr/bin/env python3
"""Clear old Data Cache entries to allow new ones with correct TTL"""

import redis
from urllib.parse import urlparse

# Using the public Redis URL from Railway
REDIS_PUBLIC_URL = "redis://default:TLqyorpIyyGclMFAOjmAjblyXwyOqLZl@nozomi.proxy.rlwy.net:55949"

def clear_data_cache():
    """Clear only the Data Cache (DB 1)"""
    
    print("🔍 Connecting to Redis...")
    parsed = urlparse(REDIS_PUBLIC_URL)
    
    # Connect to Data Cache (DB 1)
    r = redis.Redis(
        host=parsed.hostname,
        port=parsed.port,
        password=parsed.password,
        db=1,  # Data Cache
        decode_responses=True
    )
    
    # Get all keys
    keys = r.keys('*')
    print(f"📊 Found {len(keys)} keys in Data Cache")
    
    if keys:
        # Check TTL of first few keys
        short_ttl_keys = []
        for key in keys:
            ttl = r.ttl(key)
            if ttl > 0 and ttl < 3600:  # Less than 1 hour
                short_ttl_keys.append(key)
        
        print(f"⚠️  Found {len(short_ttl_keys)} keys with TTL < 1 hour")
        
        if short_ttl_keys:
            response = input("Clear these short-TTL keys? (y/n): ")
            if response.lower() == 'y':
                for key in short_ttl_keys:
                    r.delete(key)
                print(f"✅ Deleted {len(short_ttl_keys)} short-TTL keys")
            else:
                print("❌ Cancelled")
    else:
        print("✅ Data Cache is empty")

if __name__ == "__main__":
    clear_data_cache()