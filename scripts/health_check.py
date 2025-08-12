#!/usr/bin/env python
"""
Health check script for production Superset deployment
"""
import sys
import requests
import os
from urllib.parse import urljoin

def check_health():
    """Check if Superset is running and healthy"""
    base_url = os.environ.get('SUPERSET_URL', f"http://localhost:{os.environ.get('PORT', '8088')}")
    
    checks = {
        'Server Status': '/health',
        'API Status': '/api/v1/security/csrf_token/',
        'Login Page': '/login/',
    }
    
    all_healthy = True
    
    for check_name, endpoint in checks.items():
        try:
            url = urljoin(base_url, endpoint)
            response = requests.get(url, timeout=10)
            
            if response.status_code in [200, 302, 401]:  # 401 is OK for protected endpoints
                print(f"✅ {check_name}: OK (Status: {response.status_code})")
            else:
                print(f"❌ {check_name}: Failed (Status: {response.status_code})")
                all_healthy = False
        except Exception as e:
            print(f"❌ {check_name}: Error - {str(e)}")
            all_healthy = False
    
    # Check Redis if configured
    redis_url = os.environ.get('REDIS_URL')
    if redis_url:
        try:
            import redis
            r = redis.from_url(redis_url)
            r.ping()
            print("✅ Redis: Connected")
        except Exception as e:
            print(f"⚠️  Redis: {str(e)}")
    
    return all_healthy

if __name__ == "__main__":
    healthy = check_health()
    sys.exit(0 if healthy else 1)