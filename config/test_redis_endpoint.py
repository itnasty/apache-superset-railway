"""
Redis cache test endpoint for Superset
Add this to your superset_config.py to enable the test endpoint
"""

from flask import jsonify
import redis
from urllib.parse import urlparse
import os
import json
import time

def init_redis_test_endpoint(app):
    """Initialize Redis test endpoint in Superset app"""
    
    @app.route('/api/test-redis-cache')
    def test_redis_cache():
        """Test endpoint to verify Redis caching is working"""
        
        results = {
            "timestamp": time.time(),
            "redis_configured": False,
            "redis_connected": False,
            "cache_databases": {},
            "test_operations": {},
            "errors": []
        }
        
        redis_url = os.environ.get("REDIS_URL")
        
        if not redis_url:
            results["errors"].append("REDIS_URL environment variable not set")
            return jsonify(results), 500
        
        results["redis_configured"] = True
        
        try:
            # Parse Redis URL
            parsed = urlparse(redis_url)
            
            # Test basic connection
            r = redis.Redis(
                host=parsed.hostname,
                port=parsed.port or 6379,
                password=parsed.password,
                decode_responses=True
            )
            
            # Ping test
            r.ping()
            results["redis_connected"] = True
            
            # Test operations
            test_key = f"superset_test_{int(time.time())}"
            test_value = {"test": "success", "time": time.time()}
            
            # SET operation
            r.set(test_key, json.dumps(test_value), ex=60)
            results["test_operations"]["set"] = "success"
            
            # GET operation
            retrieved = r.get(test_key)
            if retrieved:
                results["test_operations"]["get"] = json.loads(retrieved)
            
            # DELETE operation
            r.delete(test_key)
            results["test_operations"]["delete"] = "success"
            
            # Check cache databases
            cache_dbs = [
                (0, "results_backend"),
                (1, "data_cache"),
                (2, "filter_state_cache"),
                (3, "explore_form_cache")
            ]
            
            for db_num, cache_name in cache_dbs:
                r_db = redis.Redis(
                    host=parsed.hostname,
                    port=parsed.port or 6379,
                    password=parsed.password,
                    db=db_num,
                    decode_responses=True
                )
                
                db_info = {
                    "key_count": r_db.dbsize(),
                    "sample_keys": []
                }
                
                # Get sample keys
                if db_info["key_count"] > 0:
                    for key in list(r_db.scan_iter(count=3))[:3]:
                        db_info["sample_keys"].append({
                            "key": key[:50] + "..." if len(key) > 50 else key,
                            "ttl": r_db.ttl(key)
                        })
                
                results["cache_databases"][cache_name] = db_info
            
            return jsonify(results), 200
            
        except redis.ConnectionError as e:
            results["errors"].append(f"Redis connection error: {str(e)}")
            return jsonify(results), 500
        except Exception as e:
            results["errors"].append(f"Unexpected error: {str(e)}")
            return jsonify(results), 500

# Add this function call to your superset_config.py:
# from test_redis_endpoint import init_redis_test_endpoint
# FLASK_APP_MUTATOR = lambda app: init_redis_test_endpoint(app)