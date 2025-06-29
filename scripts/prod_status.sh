#!/bin/bash
# GOLEM Production Status Check
# Quick overview of production deployment

echo "🤖 GOLEM Production Status"
echo "=========================="
echo ""

# Container status
echo "📦 Container Status:"
docker ps --filter "name=golem" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

# Resource usage
echo "💻 Resource Usage:"
docker stats golem --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
echo ""

# Health check
echo "🏥 Health Status:"
HEALTH=$(docker inspect golem 2>/dev/null | jq -r '.[0].State.Health.Status' || echo "unknown")
echo "Health: $HEALTH"
echo ""

# Recent errors
echo "❌ Recent Errors (last 5 min):"
ERROR_COUNT=$(docker logs golem --since 5m 2>&1 | grep -c "ERROR" || echo "0")
echo "Error count: $ERROR_COUNT"
if [ "$ERROR_COUNT" -gt "0" ]; then
    echo "Last 3 errors:"
    docker logs golem --since 5m 2>&1 | grep "ERROR" | tail -3
fi
echo ""

# Bot info
echo "🤖 Bot Info:"
docker logs golem 2>&1 | grep -E "(online|Servers:|GOLEM initialized)" | tail -5
echo ""

# Memory snapshots (if DB connected)
echo "💾 Memory Snapshots:"
echo "Would check: SELECT COUNT(*) FROM memory_snapshots (when DB connected)"
echo ""

# Quick commands test
echo "✅ Quick Test Commands:"
echo "  docker exec golem python -c 'print(\"Python OK\")'"
echo "  docker exec golem python healthcheck.py"
echo ""

echo "📊 Full logs: docker logs -f golem"
echo "📈 Live stats: docker stats golem"