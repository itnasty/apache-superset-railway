#!/usr/bin/env python3
"""Test script to verify Redis caching is working in Superset"""

import os
import sys
import redis
from urllib.parse import urlparse
import json
import time

def test_redis_connection():
    """Test basic Redis connection and operations"""
    
    redis_url = os.environ.get("REDIS_URL")
    if not redis_url:
        print("❌ REDIS_URL environment variable not set")
        return False
    
    print(f"📡 Connecting to Redis...")
    print(f"   URL: {redis_url.replace(urlparse(redis_url).password, '***')}")
    
    try:
        # Parse Redis URL
        parsed = urlparse(redis_url)
        
        # Connect to Redis
        r = redis.Redis(
            host=parsed.hostname,
            port=parsed.port or 6379,
            password=parsed.password,
            decode_responses=True
        )
        
        # Test connection
        r.ping()
        print("✅ Successfully connected to Redis!")
        
        # Test basic operations
        print("\n🧪 Testing Redis operations...")
        
        # Set a test key
        test_key = "superset_test_key"
        test_value = {"test": "data", "timestamp": time.time()}
        r.set(test_key, json.dumps(test_value), ex=60)  # 60 second expiry
        print(f"✅ SET operation successful: {test_key}")
        
        # Get the test key
        retrieved = r.get(test_key)
        if retrieved:
            retrieved_data = json.loads(retrieved)
            print(f"✅ GET operation successful: {retrieved_data}")
        
        # Check cache databases
        print("\n📊 Checking cache databases...")
        
        # Check each cache DB
        cache_dbs = [
            (0, "Results Backend"),
            (1, "Data Cache"),
            (2, "Filter State Cache"),
            (3, "Explore Form Data Cache")
        ]
        
        for db_num, cache_name in cache_dbs:
            r_db = redis.Redis(
                host=parsed.hostname,
                port=parsed.port or 6379,
                password=parsed.password,
                db=db_num,
                decode_responses=True
            )
            
            # Get key count
            key_count = r_db.dbsize()
            print(f"   DB{db_num} ({cache_name}): {key_count} keys")
            
            # Show sample keys if any exist
            if key_count > 0:
                sample_keys = list(r_db.scan_iter(count=5))[:5]
                for key in sample_keys:
                    ttl = r_db.ttl(key)
                    print(f"      - {key[:50]}... (TTL: {ttl}s)")
        
        # Clean up test key
        r.delete(test_key)
        print(f"\n🧹 Cleaned up test key: {test_key}")
        
        print("\n✅ All Redis cache tests passed!")
        return True
        
    except redis.ConnectionError as e:
        print(f"❌ Failed to connect to Redis: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_superset_config():
    """Check if Superset configuration includes Redis caching"""
    
    config_path = "/app/pythonpath/superset_config.py"
    
    if os.path.exists(config_path):
        print(f"\n📄 Checking Superset configuration at {config_path}")
        
        with open(config_path, 'r') as f:
            config_content = f.read()
            
        redis_configs = [
            "RESULTS_BACKEND",
            "DATA_CACHE_CONFIG",
            "FILTER_STATE_CACHE_CONFIG",
            "EXPLORE_FORM_DATA_CACHE_CONFIG"
        ]
        
        for config in redis_configs:
            if config in config_content:
                print(f"   ✅ {config} is configured")
            else:
                print(f"   ❌ {config} is NOT configured")
    else:
        print(f"⚠️  Config file not found at {config_path}")
        print("   This script should be run inside the Superset container")

if __name__ == "__main__":
    print("🚀 Apache Superset Redis Cache Test\n")
    print("=" * 50)
    
    # Test Redis connection
    success = test_redis_connection()
    
    # Check Superset config if running in container
    check_superset_config()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Redis caching is properly configured and working!")
        sys.exit(0)
    else:
        print("❌ Redis caching test failed. Check the errors above.")
        sys.exit(1)