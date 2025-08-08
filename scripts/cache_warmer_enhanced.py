#!/usr/bin/env python3
"""
Enhanced Cache Warming Script for Apache Superset with Tab Support
Handles multi-tab dashboards by warming all tabs individually
"""

import os
import sys
import time
import json
import logging
import argparse
from datetime import datetime, timedelta
import requests
from typing import List, Dict, Optional, Any
from urllib.parse import urlencode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SupersetTabAwareCacheWarmer:
    """Enhanced cache warmer that handles dashboard tabs"""
    
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.access_token = None
        self.csrf_token = None
        
    def authenticate(self) -> bool:
        """Authenticate with Superset API"""
        try:
            # Get CSRF token first
            login_page = self.session.get(f"{self.base_url}/login/")
            
            # Login endpoint
            login_url = f"{self.base_url}/api/v1/security/login"
            
            response = self.session.post(
                login_url,
                json={
                    "username": self.username,
                    "password": self.password,
                    "provider": "db"
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json'
                })
                logger.info("✅ Authentication successful")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    def get_dashboard_details(self, dashboard_id: int) -> Optional[Dict]:
        """Get detailed dashboard information including tabs"""
        try:
            url = f"{self.base_url}/api/v1/dashboard/{dashboard_id}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                return response.json().get('result', {})
            else:
                logger.error(f"Failed to get dashboard {dashboard_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting dashboard {dashboard_id}: {e}")
            return None
    
    def extract_tabs_from_dashboard(self, dashboard_data: Dict) -> List[Dict]:
        """Extract tab information from dashboard metadata"""
        tabs = []
        
        try:
            # Get position JSON which contains tab information
            position_json = dashboard_data.get('position_json')
            if position_json:
                if isinstance(position_json, str):
                    position_data = json.loads(position_json)
                else:
                    position_data = position_json
                
                # Look for TAB components
                for component_id, component in position_data.items():
                    if component.get('type') == 'TAB':
                        tab_info = {
                            'id': component_id,
                            'text': component.get('meta', {}).get('text', 'Unnamed Tab'),
                            'children': component.get('children', [])
                        }
                        tabs.append(tab_info)
                        logger.debug(f"Found tab: {tab_info['text']}")
            
            # If no tabs found, treat as single-tab dashboard
            if not tabs:
                logger.info("No tabs found, treating as single view dashboard")
                tabs = [{'id': 'main', 'text': 'Main', 'children': []}]
                
        except Exception as e:
            logger.error(f"Error extracting tabs: {e}")
            tabs = [{'id': 'main', 'text': 'Main', 'children': []}]
        
        return tabs
    
    def get_charts_for_tab(self, dashboard_data: Dict, tab_children: List) -> List[int]:
        """Get chart IDs that belong to a specific tab"""
        chart_ids = []
        
        try:
            position_json = dashboard_data.get('position_json')
            if position_json:
                if isinstance(position_json, str):
                    position_data = json.loads(position_json)
                else:
                    position_data = position_json
                
                # Recursively find all charts in tab children
                def find_charts(component_ids):
                    for comp_id in component_ids:
                        if comp_id in position_data:
                            component = position_data[comp_id]
                            
                            # Check if this is a chart
                            if component.get('type') == 'CHART':
                                chart_id = component.get('meta', {}).get('chartId')
                                if chart_id:
                                    chart_ids.append(chart_id)
                            
                            # Recursively check children
                            children = component.get('children', [])
                            if children:
                                find_charts(children)
                
                find_charts(tab_children)
                
        except Exception as e:
            logger.error(f"Error getting charts for tab: {e}")
        
        return chart_ids
    
    def warm_dashboard_tab(self, dashboard_id: int, tab_id: str, chart_ids: List[int], 
                          filters: Optional[Dict] = None) -> bool:
        """Warm cache for a specific dashboard tab"""
        try:
            logger.info(f"  Warming tab: {tab_id} with {len(chart_ids)} charts")
            
            # Build the dashboard URL with tab parameter
            params = {'tab': tab_id} if tab_id != 'main' else {}
            
            # Load each chart in the tab
            success_count = 0
            for chart_id in chart_ids:
                if self.warm_chart(chart_id, dashboard_id, filters):
                    success_count += 1
                time.sleep(0.2)  # Small delay between charts
            
            logger.info(f"    ✓ Warmed {success_count}/{len(chart_ids)} charts in tab")
            
            # Also warm with different time ranges
            time_ranges = ["Last day", "Last week", "Last month"]
            for time_range in time_ranges:
                filter_params = filters or {}
                filter_params['time_range'] = time_range
                
                for chart_id in chart_ids[:3]:  # Warm first 3 charts with each time range
                    self.warm_chart(chart_id, dashboard_id, filter_params)
                
                time.sleep(0.3)
            
            return True
            
        except Exception as e:
            logger.error(f"Error warming tab {tab_id}: {e}")
            return False
    
    def warm_chart(self, chart_id: int, dashboard_id: Optional[int] = None, 
                   filters: Optional[Dict] = None) -> bool:
        """Warm cache for a specific chart"""
        try:
            # Use the chart data API endpoint
            url = f"{self.base_url}/api/v1/chart/{chart_id}/data"
            
            # Build query parameters
            params = {}
            if dashboard_id:
                params['dashboard_id'] = dashboard_id
            
            # Build form data
            form_data = {
                "force": False,  # Use cache if available
            }
            
            if filters:
                form_data['filters'] = filters
            
            # Add form_data to params
            params['form_data'] = json.dumps({"slice_id": chart_id})
            
            # Make the request
            response = self.session.post(
                url + "?" + urlencode(params),
                json=form_data,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
            
            if response.status_code == 200:
                logger.debug(f"      ✓ Chart {chart_id} cached")
                return True
            else:
                logger.warning(f"      ✗ Chart {chart_id} failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error warming chart {chart_id}: {e}")
            return False
    
    def warm_dashboard_with_tabs(self, dashboard_id: int) -> bool:
        """Warm a dashboard including all its tabs"""
        try:
            logger.info(f"\n🔥 Warming dashboard {dashboard_id}...")
            
            # Get dashboard details
            dashboard_data = self.get_dashboard_details(dashboard_id)
            if not dashboard_data:
                logger.error(f"Could not get dashboard {dashboard_id} details")
                return False
            
            dashboard_name = dashboard_data.get('dashboard_title', 'Unknown')
            logger.info(f"📊 Dashboard: {dashboard_name}")
            
            # Extract tabs
            tabs = self.extract_tabs_from_dashboard(dashboard_data)
            logger.info(f"📑 Found {len(tabs)} tabs")
            
            # Get all charts
            all_chart_ids = []
            if dashboard_data.get('slices'):
                all_chart_ids = [s.get('slice_id') for s in dashboard_data.get('slices', []) 
                               if s.get('slice_id')]
            
            # Warm each tab
            for i, tab in enumerate(tabs, 1):
                logger.info(f"\n  Tab {i}/{len(tabs)}: {tab['text']}")
                
                # Get charts for this tab
                if tab['children']:
                    tab_chart_ids = self.get_charts_for_tab(dashboard_data, tab['children'])
                else:
                    # If no specific tab children, use all charts
                    tab_chart_ids = all_chart_ids
                
                if tab_chart_ids:
                    self.warm_dashboard_tab(dashboard_id, tab['id'], tab_chart_ids)
                else:
                    logger.warning(f"    No charts found in tab {tab['text']}")
                
                time.sleep(0.5)  # Pause between tabs
            
            logger.info(f"✅ Dashboard {dashboard_id} ({dashboard_name}) fully warmed!")
            return True
            
        except Exception as e:
            logger.error(f"Error warming dashboard {dashboard_id}: {e}")
            return False
    
    def get_dashboards(self) -> List[Dict]:
        """Get list of all dashboards"""
        try:
            url = f"{self.base_url}/api/v1/dashboard/"
            params = {
                'q': json.dumps({
                    'page_size': 100,
                    'page': 0
                })
            }
            
            response = self.session.get(url, params=params)
            
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
    
    def warm_all_dashboards(self) -> None:
        """Warm all dashboards including all tabs"""
        dashboards = self.get_dashboards()
        
        if not dashboards:
            logger.warning("No dashboards found to warm")
            return
        
        logger.info(f"\n🚀 Starting enhanced cache warming for {len(dashboards)} dashboards...")
        logger.info("=" * 60)
        
        success_count = 0
        for dashboard in dashboards:
            dash_id = dashboard.get('id')
            
            if self.warm_dashboard_with_tabs(dash_id):
                success_count += 1
            
            time.sleep(2)  # Pause between dashboards
        
        logger.info("\n" + "=" * 60)
        logger.info(f"✅ Enhanced cache warming complete: {success_count}/{len(dashboards)} dashboards warmed")
    
    def warm_specific_dashboards(self, dashboard_ids: List[int]) -> None:
        """Warm specific dashboards by ID"""
        logger.info(f"\n🎯 Warming {len(dashboard_ids)} specific dashboards with tab support...")
        
        success_count = 0
        for dash_id in dashboard_ids:
            if self.warm_dashboard_with_tabs(dash_id):
                success_count += 1
            time.sleep(1)
        
        logger.info(f"✅ Warmed {success_count}/{len(dashboard_ids)} dashboards successfully")
    
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
            
            # Count keys in each database
            stats = {
                "databases": {},
                "total_keys": 0
            }
            
            db_names = [
                "Results Cache",
                "Data Cache", 
                "Filter Cache",
                "Explore Cache",
                "Thumbnail Cache",
                "Metadata Cache"
            ]
            
            for db_num, db_name in enumerate(db_names):
                r_db = redis.Redis(
                    host=parsed.hostname,
                    port=parsed.port or 6379,
                    password=parsed.password,
                    db=db_num
                )
                key_count = r_db.dbsize()
                stats["databases"][db_name] = key_count
                stats["total_keys"] += key_count
            
            # Get hit rate
            info = r.info('stats')
            hits = info.get('keyspace_hits', 0)
            misses = info.get('keyspace_misses', 0)
            
            if hits + misses > 0:
                stats['hit_rate'] = (hits / (hits + misses)) * 100
            else:
                stats['hit_rate'] = 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Enhanced Superset cache warmer with tab support')
    parser.add_argument('--url', default=os.environ.get('SUPERSET_URL', 'http://localhost:8088'),
                       help='Superset base URL')
    parser.add_argument('--username', default=os.environ.get('ADMIN_USERNAME', 'admin'),
                       help='Admin username')
    parser.add_argument('--password', default=os.environ.get('ADMIN_PASSWORD', 'admin'),
                       help='Admin password')
    parser.add_argument('--dashboard-ids', type=str,
                       help='Comma-separated dashboard IDs to warm')
    parser.add_argument('--all', action='store_true',
                       help='Warm all dashboards')
    parser.add_argument('--stats', action='store_true',
                       help='Show cache statistics')
    
    args = parser.parse_args()
    
    # Initialize warmer
    warmer = SupersetTabAwareCacheWarmer(args.url, args.username, args.password)
    
    # Show initial stats
    if args.stats:
        stats = warmer.get_cache_stats()
        logger.info("\n📊 Cache Stats (Before):")
        logger.info(f"  Total Keys: {stats.get('total_keys', 0)}")
        logger.info(f"  Hit Rate: {stats.get('hit_rate', 0):.1f}%")
        for db_name, count in stats.get('databases', {}).items():
            logger.info(f"  {db_name}: {count} keys")
    
    # Authenticate
    if not warmer.authenticate():
        logger.error("Failed to authenticate")
        sys.exit(1)
    
    # Perform warming
    if args.dashboard_ids:
        dashboard_ids = [int(d.strip()) for d in args.dashboard_ids.split(',')]
        warmer.warm_specific_dashboards(dashboard_ids)
    elif args.all:
        warmer.warm_all_dashboards()
    else:
        # Default: warm first 3 dashboards
        dashboards = warmer.get_dashboards()[:3]
        if dashboards:
            dashboard_ids = [d['id'] for d in dashboards]
            warmer.warm_specific_dashboards(dashboard_ids)
    
    # Show final stats
    if args.stats:
        time.sleep(2)
        stats = warmer.get_cache_stats()
        logger.info("\n📊 Cache Stats (After):")
        logger.info(f"  Total Keys: {stats.get('total_keys', 0)}")
        logger.info(f"  Hit Rate: {stats.get('hit_rate', 0):.1f}%")
        for db_name, count in stats.get('databases', {}).items():
            logger.info(f"  {db_name}: {count} keys")

if __name__ == "__main__":
    main()