#!/usr/bin/env python3
"""Temporary Redis checker using Railway internal URL"""

import redis
from urllib.parse import urlparse

def check_redis_data():
    """Check all Redis databases for existing data"""
    
    print("🔍 Checking Redis cache status...")
    print("=" * 50)
    
    # Note: This would normally come from environment variable
    # For security, you should set REDIS_PUBLIC_URL in your environment
    print("⚠️  Using temporary connection for checking")
    print("   Please rotate Redis credentials after this check")
    print("=" * 50)
    
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
        print("   [Connection details hidden for security]")
        
    print("\n" + "=" * 50)
    print("⚠️  For security reasons, please:")
    print("   1. Set REDIS_PUBLIC_URL environment variable")
    print("   2. Use the original check_redis_data.py script")
    print("   3. Rotate your Redis credentials in Railway")

if __name__ == "__main__":
    print("🚀 Redis Data Inspector for Apache Superset\n")
    check_redis_data()