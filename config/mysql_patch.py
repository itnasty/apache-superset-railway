"""
Patch for Superset's database engine specs to ensure proper connection parameter handling.
This complements the main fixes in superset_config.py.
"""

def patch_engine_specs():
    """
    Patch database engine specs to ensure they use proper connection parameters.
    This is a safety layer on top of the main SQLAlchemy create_engine patch.
    """
    try:
        # Import all database engine specs that might need patching
        from superset.db_engine_specs.mysql import MySQLEngineSpec
        from superset.db_engine_specs.postgres import PostgresEngineSpec
        
        # Store original methods
        original_mysql_params = MySQLEngineSpec.get_engine_params
        original_postgres_params = PostgresEngineSpec.get_engine_params
        
        # Create patched version for MySQL
        @classmethod
        def patched_mysql_params(cls):
            """Ensure MySQL connections use proper pool parameters"""
            params = original_mysql_params.__func__(cls) if hasattr(original_mysql_params, '__func__') else original_mysql_params(cls)
            
            # Ensure pool_pre_ping is enabled
            params['pool_pre_ping'] = True
            
            # Ensure pool_recycle is an integer (seconds)
            if 'pool_recycle' in params:
                try:
                    params['pool_recycle'] = int(params['pool_recycle'])
                except (TypeError, ValueError):
                    params['pool_recycle'] = 1800  # Default 30 minutes
            else:
                params['pool_recycle'] = 1800
            
            return params
        
        # Create patched version for PostgreSQL
        @classmethod
        def patched_postgres_params(cls):
            """Ensure PostgreSQL connections use proper pool parameters"""
            params = original_postgres_params.__func__(cls) if hasattr(original_postgres_params, '__func__') else original_postgres_params(cls)
            
            # Ensure pool_pre_ping is enabled
            params['pool_pre_ping'] = True
            
            # Ensure pool_recycle is an integer (seconds)
            if 'pool_recycle' in params:
                try:
                    params['pool_recycle'] = int(params['pool_recycle'])
                except (TypeError, ValueError):
                    params['pool_recycle'] = 1800  # Default 30 minutes
            else:
                params['pool_recycle'] = 1800
            
            return params
        
        # Apply patches
        MySQLEngineSpec.get_engine_params = patched_mysql_params
        PostgresEngineSpec.get_engine_params = patched_postgres_params
        
        print("✅ Successfully patched MySQL and PostgreSQL engine specs")
        return True
        
    except ImportError as e:
        print(f"⚠️  Could not import database engine specs: {e}")
        print("   This is normal if Superset hasn't initialized yet")
        return False
    except Exception as e:
        print(f"❌ Error patching engine specs: {e}")
        return False

# Try to apply the patch immediately when this module is imported
# If it fails (because Superset isn't initialized yet), that's okay
patch_engine_specs()
