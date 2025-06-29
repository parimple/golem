#!/bin/bash
# Setup monitoring for GOLEM production

echo "Setting up GOLEM monitoring..."

# Create log directory
mkdir -p /var/log/golem

# Add cron job for monitoring (every 5 minutes)
CRON_CMD="*/5 * * * * /opt/golem/scripts/monitor_prod.sh >> /var/log/golem/monitor.log 2>&1"

# Check if cron job already exists
if ! crontab -l 2>/dev/null | grep -q "monitor_prod.sh"; then
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
    echo "✅ Monitoring cron job added"
else
    echo "⚠️  Monitoring cron job already exists"
fi

# Setup log rotation
cat > /etc/logrotate.d/golem << EOF
/var/log/golem/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
EOF

echo "✅ Log rotation configured"

# Create systemd service (optional)
cat > /etc/systemd/system/golem-monitor.service << EOF
[Unit]
Description=GOLEM Production Monitor
After=docker.service

[Service]
Type=oneshot
ExecStart=/opt/golem/scripts/monitor_prod.sh
StandardOutput=append:/var/log/golem/monitor.log
StandardError=append:/var/log/golem/monitor.log

[Install]
WantedBy=multi-user.target
EOF

# Create timer for systemd (alternative to cron)
cat > /etc/systemd/system/golem-monitor.timer << EOF
[Unit]
Description=Run GOLEM Monitor every 5 minutes
Requires=golem-monitor.service

[Timer]
OnBootSec=5min
OnUnitActiveSec=5min

[Install]
WantedBy=timers.target
EOF

echo "✅ Systemd service created (optional alternative to cron)"
echo ""
echo "To use systemd instead of cron:"
echo "  systemctl enable golem-monitor.timer"
echo "  systemctl start golem-monitor.timer"
echo ""
echo "Monitoring setup complete!"