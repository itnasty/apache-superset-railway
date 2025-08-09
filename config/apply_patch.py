#!/usr/bin/env python3
"""
Apply the cache timeout patch after Superset initialization
This should be run after the Flask app is created
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, '/app')

def apply_patches():
    """Apply all patches after app initialization"""
    try:
        # Import Superset app
        from superset.app import create_app
        
        # Create app instance
        app = create_app()
        
        # Apply patches within app context
        with app.app_context():
            from cache_timeout_patch import apply_cache_timeout_patch
            if apply_cache_timeout_patch():
                print("✅ Cache timeout patch applied successfully!")
                return True
            else:
                print("⚠️ Cache timeout patch failed to apply")
                return False
                
    except Exception as e:
        print(f"❌ Error applying patches: {e}")
        return False

if __name__ == "__main__":
    apply_patches()