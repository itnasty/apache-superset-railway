#!/usr/bin/env python3
"""
Cache Warming Script for Apache Superset
Preloads frequently accessed dashboards and queries into Redis cache
"""

import os
import sys
import time
import json
import logging
import argparse
from datetime import datetime, timedelta
import requests
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SupersetCacheWarmer:
    """Warm Redis cache for Superset dashboards and queries"""
    
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.access_token = None
        
    def authenticate(self) -> bool:
        """Authenticate with Superset API"""
        try:
            # Login endpoint
            login_url = f"{self.base_url}/api/v1/security/login"
            
            response = self.session.post(
                login_url,
                json={
                    "username": self.username,
                    "password": self.password,
                    "provider": "db"
                }
            )
            
            if response.status_code == 200:
                self.access_token = response.json().get('access_token')
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                logger.info("✅ Authentication successful")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    def get_dashboards(self) -> List[Dict]:
        """Get list of all dashboards"""
        try:
            url = f"{self.base_url}/api/v1/dashboard/"
            response = self.session.get(url)
            
            if response.status_code == 200:
                dashboards = response.json().get('result', [])
                logger.info(f"Found {len(dashboards)} dashboards")
                return dashboards
            else:
                logger.error(f"Failed to get dashboards: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting dashboards: {e}")
            return []
    
    def warm_dashboard(self, dashboard_id: int, filters: Optional[Dict] = None) -> bool:
        """Warm cache for a specific dashboard"""
        try:
            # Get dashboard data
            url = f"{self.base_url}/api/v1/dashboard/{dashboard_id}"
            
            logger.info(f"Warming dashboard {dashboard_id}...")
            
            # Load dashboard metadata
            response = self.session.get(url)
            if response.status_code != 200:
                logger.error(f"Failed to load dashboard {dashboard_id}")
                return False
            
            dashboard_data = response.json().get('result', {})
            
            # Get dashboard charts
            charts_url = f"{self.base_url}/api/v1/dashboard/{dashboard_id}/charts"
            charts_response = self.session.get(charts_url)
            
            if charts_response.status_code == 200:
                charts = charts_response.json().get('result', [])
                logger.info(f"  Found {len(charts)} charts in dashboard {dashboard_id}")
                
                # Warm each chart
                for chart in charts:
                    self.warm_chart(chart.get('id'), filters)
            
            # Load dashboard with different time ranges
            time_ranges = [
                "Last day",
                "Last week",
                "Last month",
                "Last quarter",
                "Last year"
            ]
            
            for time_range in time_ranges:
                filter_params = filters or {}
                filter_params['time_range'] = time_range
                
                # Trigger dashboard data load
                data_url = f"{self.base_url}/api/v1/dashboard/{dashboard_id}/data"
                self.session.post(data_url, json=filter_params)
                
                time.sleep(0.5)  # Be nice to the server
            
            logger.info(f"✅ Dashboard {dashboard_id} warmed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error warming dashboard {dashboard_id}: {e}")
            return False
    
    def warm_chart(self, chart_id: int, filters: Optional[Dict] = None) -> bool:
        """Warm cache for a specific chart"""
        try:
            url = f"{self.base_url}/api/v1/chart/{chart_id}/data"
            
            # Default form data
            form_data = {
                "force": False,  # Use cache if available
                "filters": filters or {}
            }
            
            response = self.session.post(url, json=form_data)
            
            if response.status_code == 200:
                logger.debug(f"    Chart {chart_id} cached")
                return True
            else:
                logger.warning(f"    Chart {chart_id} failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error warming chart {chart_id}: {e}")
            return False
    
    def warm_critical_dashboards(self, dashboard_ids: List[int]) -> None:
        """Warm specific critical dashboards"""
        logger.info(f"Warming {len(dashboard_ids)} critical dashboards...")
        
        for dash_id in dashboard_ids:
            self.warm_dashboard(dash_id)
            time.sleep(1)  # Pause between dashboards
    
    def warm_all_dashboards(self) -> None:
        """Warm all dashboards in the system"""
        dashboards = self.get_dashboards()
        
        logger.info(f"Starting cache warming for {len(dashboards)} dashboards...")
        
        success_count = 0
        for dashboard in dashboards:
            dash_id = dashboard.get('id')
            dash_name = dashboard.get('dashboard_title', 'Unknown')
            
            logger.info(f"Processing: {dash_name} (ID: {dash_id})")
            
            if self.warm_dashboard(dash_id):
                success_count += 1
            
            time.sleep(2)  # Pause between dashboards
        
        logger.info(f"✅ Cache warming complete: {success_count}/{len(dashboards)} successful")
    
    def warm_recent_queries(self, hours: int = 24) -> None:
        """Re-run recent queries to warm cache"""
        try:
            # Get recent queries from SQL Lab
            url = f"{self.base_url}/api/v1/query/"
            
            # Filter for recent queries
            since = datetime.now() - timedelta(hours=hours)
            params = {
                "filters": [
                    {
                        "col": "start_time",
                        "opr": "gt",
                        "value": since.isoformat()
                    }
                ]
            }
            
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                queries = response.json().get('result', [])
                logger.info(f"Found {len(queries)} recent queries")
                
                for query in queries[:20]:  # Limit to 20 most recent
                    sql = query.get('sql')
                    database_id = query.get('database_id')
                    
                    if sql and database_id:
                        # Re-run query to cache result
                        self.run_query(sql, database_id)
                        time.sleep(1)
                        
        except Exception as e:
            logger.error(f"Error warming recent queries: {e}")
    
    def run_query(self, sql: str, database_id: int) -> bool:
        """Run a SQL query to warm cache"""
        try:
            url = f"{self.base_url}/api/v1/sqllab/execute/"
            
            payload = {
                "database_id": database_id,
                "sql": sql,
                "runAsync": False,
                "schema": None
            }
            
            response = self.session.post(url, json=payload)
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error running query: {e}")
            return False
    
    def get_cache_stats(self) -> Dict:
        """Get Redis cache statistics"""
        try:
            import redis
            from urllib.parse import urlparse
            
            redis_url = os.environ.get("REDIS_URL")
            if not redis_url:
                return {}
            
            parsed = urlparse(redis_url)
            r = redis.Redis(
                host=parsed.hostname,
                port=parsed.port or 6379,
                password=parsed.password
            )
            
            info = r.info('stats')
            
            stats = {
                "total_connections": info.get('total_connections_received', 0),
                "total_commands": info.get('total_commands_processed', 0),
                "keyspace_hits": info.get('keyspace_hits', 0),
                "keyspace_misses": info.get('keyspace_misses', 0),
                "hit_rate": 0
            }
            
            if stats['keyspace_hits'] + stats['keyspace_misses'] > 0:
                stats['hit_rate'] = stats['keyspace_hits'] / (
                    stats['keyspace_hits'] + stats['keyspace_misses']
                ) * 100
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Warm Superset Redis cache')
    parser.add_argument('--url', default=os.environ.get('SUPERSET_URL', 'http://localhost:8088'),
                       help='Superset base URL')
    parser.add_argument('--username', default=os.environ.get('ADMIN_USERNAME', 'admin'),
                       help='Admin username')
    parser.add_argument('--password', default=os.environ.get('ADMIN_PASSWORD', 'admin'),
                       help='Admin password')
    parser.add_argument('--critical-only', action='store_true',
                       help='Only warm critical dashboards')
    parser.add_argument('--dashboard-ids', type=str,
                       help='Comma-separated list of dashboard IDs to warm')
    parser.add_argument('--recent-queries', action='store_true',
                       help='Warm cache with recent queries')
    parser.add_argument('--stats', action='store_true',
                       help='Show cache statistics')
    
    args = parser.parse_args()
    
    # Initialize warmer
    warmer = SupersetCacheWarmer(args.url, args.username, args.password)
    
    # Show cache stats before warming
    if args.stats:
        stats_before = warmer.get_cache_stats()
        logger.info(f"Cache stats before: Hit rate: {stats_before.get('hit_rate', 0):.1f}%")
    
    # Authenticate
    if not warmer.authenticate():
        logger.error("Failed to authenticate with Superset")
        sys.exit(1)
    
    # Perform cache warming
    if args.dashboard_ids:
        # Warm specific dashboards
        dashboard_ids = [int(d.strip()) for d in args.dashboard_ids.split(',')]
        warmer.warm_critical_dashboards(dashboard_ids)
        
    elif args.critical_only:
        # Warm critical dashboards (customize these IDs)
        critical_dashboards = [1, 2, 3]  # Replace with your dashboard IDs
        warmer.warm_critical_dashboards(critical_dashboards)
        
    elif args.recent_queries:
        # Warm recent queries
        warmer.warm_recent_queries()
        
    else:
        # Warm all dashboards
        warmer.warm_all_dashboards()
    
    # Show cache stats after warming
    if args.stats:
        time.sleep(2)
        stats_after = warmer.get_cache_stats()
        logger.info(f"Cache stats after: Hit rate: {stats_after.get('hit_rate', 0):.1f}%")
        
        improvement = stats_after.get('hit_rate', 0) - stats_before.get('hit_rate', 0)
        logger.info(f"Hit rate improvement: {improvement:.1f}%")
    
    logger.info("✅ Cache warming complete!")

if __name__ == "__main__":
    main()