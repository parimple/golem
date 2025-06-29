# 🚀 GOLEM Production Deployment Guide

## Prerequisites

- GitHub repository with Actions enabled
- Docker registry access
- Production VPS with Docker installed
- Discord bot token for production

## 1. GitHub Secrets Configuration

Add these secrets to your GitHub repository:

```
DISCORD_TOKEN_PROD      # Production Discord bot token
DB_URL_PROD            # PostgreSQL connection string
DOCKER_REGISTRY_TOKEN  # Registry authentication token
DISCORD_WEBHOOK        # Webhook for CI/CD notifications
DEV_HOST              # Dev server hostname
DEV_USER              # Dev server SSH user
DEV_SSH_KEY           # Dev server SSH private key
```

## 2. Initial Deploy

```bash
# SSH to production server
ssh golem-prod

# Pull latest image
docker pull registry/golem:latest

# Stop existing container (if any)
docker stop golem || true
docker rm golem || true

# Run new container
docker run -d \
  --name golem \
  --restart=always \
  --env-file .env.prod \
  -v /var/log/golem:/app/logs \
  registry/golem:latest
```

## 3. Monitoring Checklist

First 10 minutes:
- [ ] Check container is running: `docker ps`
- [ ] Check logs: `docker logs -f golem`
- [ ] Monitor resources: `docker stats golem`
- [ ] Verify Discord connection in #golem-monitoring
- [ ] Test basic commands: `,help`, `,ping`, `,status`

Resource thresholds:
- Memory > 500MB: Consider scaling
- CPU > 80%: Check for runaway processes
- Error rate > 1%: Check logs for issues

## 4. Canary Rollout

```bash
# On main server, run both versions
docker run -d \
  --name golem-canary \
  --env COMMAND_PREFIX=",dev" \
  --env-file .env.prod \
  registry/golem:latest

# Monitor for 24h
# If stable, switch production
```

## 5. Database Verification

```sql
-- Check memory snapshots
SELECT COUNT(*), MAX(created_at) 
FROM memory_snapshots;

-- Check empty echo percentage
SELECT 
  (COUNT(CASE WHEN content = '' THEN 1 END)::float / COUNT(*)) * 100 as empty_percentage
FROM echoes;
```

## 6. Rollback Procedure

If issues arise:
```bash
# Quick rollback
docker stop golem
docker run -d \
  --name golem \
  --restart=always \
  --env-file .env.prod \
  registry/golem:previous-tag
```

## 7. Health Checks

Automated checks every 5 minutes:
- Memory usage
- CPU usage  
- Error rate
- Response time

Manual checks:
```bash
# Container health
docker inspect golem | jq '.[0].State.Health'

# Resource usage
docker stats golem --no-stream

# Recent logs
docker logs golem --tail 100 | grep ERROR
```

## 8. Post-Deploy

After 72 hours:
1. Analyze top errors: `docker logs golem | grep ERROR | sort | uniq -c | sort -nr | head -10`
2. Check user feedback from Discord
3. Plan v1.0.1 fixes
4. Tag release: `git tag -a v1.0.1 -m "First production fixes"`

## Troubleshooting

### High Memory Usage
```bash
# Increase memory limit
docker run -d \
  --name golem \
  --memory="1g" \
  --memory-swap="2g" \
  ...
```

### Connection Issues
- Verify Discord token is correct
- Check network connectivity
- Ensure firewall allows outbound HTTPS

### Database Issues
- Check connection string in .env.prod
- Verify database is accessible
- Check for migration issues

## Support

- Monitor channel: #golem-monitoring
- Logs location: `/var/log/golem/`
- Metrics dashboard: (to be configured)

---
Remember: **Move fast, but monitor everything!** 🚀