#!/bin/bash

# Script to apply cache timeout fix to your forked Superset

echo "🔧 Applying cache timeout fix to forked Superset..."
echo "================================================"

# Check if we have a local clone of your fork
if [ ! -d "superset-fork" ]; then
    echo "❌ Please clone your forked Superset repository first:"
    echo "   git clone https://github.com/YOUR_USERNAME/superset.git superset-fork"
    exit 1
fi

cd superset-fork

echo "📝 Modifying query_context_processor.py..."
# Find the cache_timeout method and add our custom logic
cat > /tmp/cache_fix.py << 'EOF'
import sys
import re

file_path = sys.argv[1]
with open(file_path, 'r') as f:
    content = f.read()

# Find the cache_timeout method
pattern = r'(def cache_timeout\(self\) -> int:.*?)(if cache_timeout_rv := self\._query_context\.get_cache_timeout\(\):.*?return cache_timeout_rv)'
replacement = r'''\1\2
        
        # Check for CHART_DATA_CACHE_TIMEOUT first (Custom fix for Railway)
        if chart_data_timeout := current_app.config.get("CHART_DATA_CACHE_TIMEOUT"):
            logger.info(f"Using CHART_DATA_CACHE_TIMEOUT: {chart_data_timeout}")
            return chart_data_timeout
        if data_cache_timeout := current_app.config.get("DATA_CACHE_TIMEOUT"):
            logger.info(f"Using DATA_CACHE_TIMEOUT: {data_cache_timeout}")
            return data_cache_timeout'''

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
    
print("✅ Fixed query_context_processor.py")
EOF

python3 /tmp/cache_fix.py superset/common/query_context_processor.py

echo "📝 Adding configuration variables to config.py..."
# Add the new config variables if they don't exist
if ! grep -q "CHART_DATA_CACHE_TIMEOUT" superset/config.py; then
    cat >> superset/config.py << 'EOF'

# Chart data API cache timeout (can be overridden in superset_config.py)
# Added for Railway deployment fix
CHART_DATA_CACHE_TIMEOUT = None  # Will use DATA_CACHE_CONFIG timeout if not set
DATA_CACHE_TIMEOUT = None  # Will use DATA_CACHE_CONFIG timeout if not set
EOF
    echo "✅ Added cache timeout configuration variables"
else
    echo "ℹ️  Cache timeout variables already exist"
fi

echo ""
echo "✅ Cache timeout fix applied successfully!"
echo ""
echo "Next steps:"
echo "1. Commit these changes to your fork:"
echo "   cd superset-fork"
echo "   git add -A"
echo "   git commit -m 'Fix: Respect CHART_DATA_CACHE_TIMEOUT configuration'"
echo "   git push origin main"
echo ""
echo "2. Build your custom Docker image:"
echo "   docker build -f Dockerfile.custom -t your-dockerhub/superset-fixed:latest ."
echo ""
echo "3. Update your Dockerfile to use your custom image"
echo "4. Deploy to Railway"