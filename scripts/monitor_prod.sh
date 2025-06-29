#!/bin/bash
# GOLEM Production Monitor Script
# Runs every 5 minutes via cron

CONTAINER_NAME="golem"
WEBHOOK_URL="${DISCORD_WEBHOOK}"
MAX_MEMORY_MB=500
MAX_CPU_PERCENT=80
ERROR_THRESHOLD=10

# Function to send Discord alert
send_alert() {
    local title="$1"
    local message="$2"
    local color="$3"
    
    if [ -n "$WEBHOOK_URL" ]; then
        curl -s -X POST "$WEBHOOK_URL" \
            -H "Content-Type: application/json" \
            -d "{
                \"embeds\": [{
                    \"title\": \"$title\",
                    \"description\": \"$message\",
                    \"color\": $color,
                    \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%S.000Z)\"
                }]
            }"
    fi
}

# Check if container is running
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    send_alert "🚨 GOLEM Down!" "Container is not running!" 15158332
    exit 1
fi

# Get container stats
STATS=$(docker stats "$CONTAINER_NAME" --no-stream --format "{{.MemUsage}} {{.CPUPerc}}")
MEMORY=$(echo "$STATS" | awk '{print $1}' | sed 's/MiB//')
CPU=$(echo "$STATS" | awk '{print $NF}' | sed 's/%//')

# Check memory
if (( $(echo "$MEMORY > $MAX_MEMORY_MB" | bc -l) )); then
    send_alert "⚠️ High Memory Usage" "Memory: ${MEMORY}MB (threshold: ${MAX_MEMORY_MB}MB)" 16776960
fi

# Check CPU
if (( $(echo "$CPU > $MAX_CPU_PERCENT" | bc -l) )); then
    send_alert "⚠️ High CPU Usage" "CPU: ${CPU}% (threshold: ${MAX_CPU_PERCENT}%)" 16776960
fi

# Check recent errors
ERROR_COUNT=$(docker logs "$CONTAINER_NAME" --since 5m 2>&1 | grep -c "ERROR")
if [ "$ERROR_COUNT" -gt "$ERROR_THRESHOLD" ]; then
    send_alert "⚠️ High Error Rate" "Found $ERROR_COUNT errors in last 5 minutes" 15158332
fi

# Health check
HEALTH=$(docker inspect "$CONTAINER_NAME" | jq -r '.[0].State.Health.Status')
if [ "$HEALTH" != "healthy" ]; then
    send_alert "⚠️ Health Check Failed" "Container health status: $HEALTH" 15158332
fi

echo "$(date): Memory: ${MEMORY}MB, CPU: ${CPU}%, Errors: $ERROR_COUNT, Health: $HEALTH"