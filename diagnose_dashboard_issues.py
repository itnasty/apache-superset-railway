# Railway Debug Script for Dashboard Issues
# Run this to diagnose network errors in dashboards

import requests
import json
import os

# Get your Superset URL and credentials
SUPERSET_URL = os.environ.get("SUPERSET_URL", "https://your-app.railway.app")
USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")

def diagnose_superset():
    print("🔍 Diagnosing Superset Dashboard Issues...")
    print("=" * 80)
    
    # 1. Test basic connectivity
    print("\n1. Testing basic connectivity...")
    try:
        response = requests.get(f"{SUPERSET_URL}/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # 2. Test authentication
    print("\n2. Testing authentication...")
    try:
        login_data = {
            "username": USERNAME,
            "password": PASSWORD,
            "provider": "db"
        }
        response = requests.post(
            f"{SUPERSET_URL}/api/v1/security/login",
            json=login_data
        )
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"✅ Authentication successful")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return
    
    # 3. Test dashboard list
    print("\n3. Testing dashboard list endpoint...")
    try:
        response = requests.get(
            f"{SUPERSET_URL}/api/v1/dashboard/",
            headers=headers
        )
        print(f"✅ Dashboard list: {response.status_code}")
        dashboards = response.json()
        print(f"   Found {dashboards.get('count', 0)} dashboards")
    except Exception as e:
        print(f"❌ Dashboard list error: {e}")
    
    # 4. Test chart data endpoint
    print("\n4. Testing chart data endpoint...")
    try:
        # This is a test payload - adjust based on your chart
        test_payload = {
            "datasource": {"id": 1, "type": "table"},
            "queries": [{
                "columns": [],
                "metrics": [],
                "orderby": [],
                "row_limit": 10
            }]
        }
        response = requests.post(
            f"{SUPERSET_URL}/api/v1/chart/data",
            headers=headers,
            json=test_payload
        )
        print(f"   Chart data endpoint: {response.status_code}")
        if response.status_code != 200:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Chart data error: {e}")
    
    # 5. Check CORS headers
    print("\n5. Checking CORS headers...")
    try:
        response = requests.options(
            f"{SUPERSET_URL}/api/v1/chart/data",
            headers={
                "Origin": SUPERSET_URL,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "authorization,content-type"
            }
        )
        print(f"   OPTIONS request: {response.status_code}")
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
        }
        for header, value in cors_headers.items():
            if value:
                print(f"   ✅ {header}: {value}")
            else:
                print(f"   ❌ {header}: Not set")
    except Exception as e:
        print(f"❌ CORS check error: {e}")
    
    print("\n" + "=" * 80)
    print("Diagnosis complete!")
    print("\nRecommendations:")
    print("1. If health check fails: Check if Superset is running")
    print("2. If authentication fails: Verify admin credentials")
    print("3. If CORS headers missing: Update superset_config.py")
    print("4. If chart data fails: Check database connections")

if __name__ == "__main__":
    diagnose_superset()
