#!/usr/bin/env python3
"""Check Redis data directly using the public URL"""

import redis
from urllib.parse import urlparse
import json

# Using the public Redis URL from Railway
REDIS_PUBLIC_URL = "redis://default:TLqyorpIyyGclMFAOjmAjblyXwyOqLZl@nozomi.proxy.rlwy.net:55949"

def check_redis_data():
    """Check all Redis databases for existing data"""
    
    print("🔍 Connecting to Redis via public URL...")
    print(f"   Host: nozomi.proxy.rlwy.net:55949")
    
    parsed = urlparse(REDIS_PUBLIC_URL)
    
    # Check each database
    databases = {
        0: "Results Backend (Query Cache)",
        1: "Data Cache",
        2: "Filter State Cache", 
        3: "Explore Form Cache"
    }
    
    total_keys = 0
    
    for db_num, db_name in databases.items():
        print(f"\n📊 Database {db_num}: {db_name}")
        print("-" * 50)
        
        try:
            r = redis.Redis(
                host=parsed.hostname,
                port=parsed.port,
                password=parsed.password,
                db=db_num,
                decode_responses=True
            )
            
            # Get database size
            db_size = r.dbsize()
            total_keys += db_size
            print(f"   Total keys: {db_size}")
            
            if db_size > 0:
                # Get all keys (limit to first 20 for display)
                keys = []
                for key in r.scan_iter():
                    keys.append(key)
                    if len(keys) >= 20:
                        break
                
                print(f"\n   Sample keys (showing up to 20):")
                for key in keys:
                    try:
                        # Get key type and TTL
                        key_type = r.type(key)
                        ttl = r.ttl(key)
                        
                        # Get value preview based on type
                        value_preview = ""
                        if key_type == "string":
                            value = r.get(key)
                            if value:
                                value_preview = value[:100] + "..." if len(value) > 100 else value
                        elif key_type == "hash":
                            value_preview = f"Hash with {r.hlen(key)} fields"
                        elif key_type == "list":
                            value_preview = f"List with {r.llen(key)} items"
                        elif key_type == "set":
                            value_preview = f"Set with {r.scard(key)} members"
                        
                        print(f"      • {key[:60]}...")
                        print(f"        Type: {key_type}, TTL: {ttl}s")
                        if value_preview:
                            print(f"        Preview: {value_preview[:80]}...")
                            
                    except Exception as e:
                        print(f"      • {key} (Error reading: {e})")
                
                if db_size > 20:
                    print(f"\n   ... and {db_size - 20} more keys")
                    
        except redis.ConnectionError as e:
            print(f"   ❌ Connection error: {e}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📈 Total keys across all databases: {total_keys}")
    
    if total_keys > 0:
        print("✅ Redis cache is being used by Superset!")
    else:
        print("⚠️  No cached data found yet. Try loading some dashboards in Superset.")

if __name__ == "__main__":
    print("🚀 Redis Data Inspector for Apache Superset\n")
    print("=" * 50)
    
    try:
        check_redis_data()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")