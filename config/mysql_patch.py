"""
Patch for Superset's MySQL engine spec to fix pool_recycle issue.
This must be imported BEFORE Superset initializes its database engine specs.
"""
from datetime import timedelta

def patch_mysql_engine_spec():
    """
    Monkey patch the MySQL engine spec to remove integer pool_recycle.
    This fixes the 'int' object has no attribute 'total_seconds' error.
    """
    try:
        from superset.db_engine_specs.mysql import MySQLEngineSpec
        
        # Store the original get_engine_params method
        original_get_engine_params = MySQLEngineSpec.get_engine_params
        
        # Create a new method that removes pool_recycle
        @classmethod
        def patched_get_engine_params(cls):
            params = original_get_engine_params.__func__(cls)
            # Remove pool_recycle to prevent the error
            params.pop('pool_recycle', None)
            # Add safe alternatives
            params['pool_pre_ping'] = True
            return params
        
        # Replace the method
        MySQLEngineSpec.get_engine_params = patched_get_engine_params
        
        print("✅ Successfully patched MySQLEngineSpec.get_engine_params")
        return True
        
    except ImportError as e:
        print(f"⚠️  Could not import MySQLEngineSpec: {e}")
        return False
    except Exception as e:
        print(f"❌ Error patching MySQLEngineSpec: {e}")
        return False

# Apply the patch immediately when this module is imported
patch_mysql_engine_spec()
