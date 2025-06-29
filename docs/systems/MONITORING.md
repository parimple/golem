# 🔧 GOLEM Performance Monitoring System

## Overview

The Monitoring system provides real-time insights into bot performance, cog health, and system resources. It tracks command usage, execution times, error rates, and system metrics to ensure optimal performance.

## Core Features

### Performance Tracking
- **Command Execution Times**: Tracks last 100 executions per command
- **Command Usage Counts**: Total uses per command
- **Error Tracking**: Errors per command
- **Cog-level Statistics**: Usage by cog
- **System Resources**: CPU and memory monitoring

### Metrics Collection
```python
self.command_times: Dict[str, deque]     # Execution times
self.command_counts: Dict[str, int]      # Usage counts
self.command_errors: Dict[str, int]      # Error counts
self.cog_command_counts: Dict[str, int]  # Commands per cog
```

## Commands

### 📊 Performance Overview
```
,performance
,perf
,stats
```
- **Requires**: Administrator permission
- Shows system resources (Memory, CPU)
- Bot statistics (Uptime, Messages, Commands)
- Connection info (Latency, Guilds, Users)

### 📦 Cog Statistics
```
,cogstats
,cogs
```
- **Requires**: Administrator permission
- Most active cogs by command usage
- Number of loaded cogs
- Overall error rate
- Cog health status

### 📈 Command Statistics
```
,commandstats [top_count]
,cmdstats [top_count]
```
- **Requires**: Administrator permission
- Top N most used commands (default: 10)
- Slowest commands by average execution time
- Commands with most errors
- Detailed performance metrics

### 🏥 Health Check
```
,health
```
- **Requires**: Administrator permission
- Quick health check of all cogs
- Shows command count per cog
- Identifies any cogs with issues
- Overall system status

## Background Monitoring

### System Monitor Task
```python
@tasks.loop(minutes=5)
async def system_monitor(self):
    # Monitors CPU and memory usage
    # Logs warnings if thresholds exceeded
```
- Runs every 5 minutes
- Warns if memory > 500MB
- Warns if CPU > 80%

## Event Listeners

### Command Tracking
```python
@commands.Cog.listener()
async def on_command(self, ctx):
    # Start timing
    # Increment counters

@commands.Cog.listener()
async def on_command_completion(self, ctx):
    # Record execution time

@commands.Cog.listener()
async def on_command_error(self, ctx, error):
    # Track errors
```

## Thresholds and Alerts

### Resource Thresholds
- **Memory Warning**: > 500 MB
- **CPU Warning**: > 80%
- **Slow Command**: > 1000ms average
- **High Error Rate**: > 10%

### Performance Targets
- Average command response: < 100ms
- Bot latency: < 100ms
- Error rate: < 1%
- Uptime: > 99.9%

## Integration with Other Systems

### Activity System
- Monitor point distribution rates
- Track level progression speed
- Identify activity patterns

### Economy System
- Track transaction volumes
- Monitor currency inflation
- Identify unusual patterns

### Voice System
- Track channel creation/deletion
- Monitor voice activity
- Resource usage by voice

## Best Practices

### For Administrators

1. **Regular Checks**:
   - Run `,health` daily
   - Check `,performance` during peak times
   - Review `,commandstats` weekly

2. **Performance Optimization**:
   - Identify slow commands
   - Monitor error-prone features
   - Track resource trends

3. **Troubleshooting**:
   - Use `,cogstats` to find problematic cogs
   - Check specific command performance
   - Monitor after updates

### Monitoring Alerts

Set up external monitoring for:
- Bot offline status
- High resource usage
- Repeated errors
- Performance degradation

## Data Retention

Current implementation:
- Command times: Last 100 executions
- All other metrics: Session lifetime
- No persistence between restarts

Future enhancements:
- Database storage for historical data
- Trend analysis over time
- Automated reports
- Grafana integration

## Example Usage

### Daily Health Check
```
,health
,performance
,cogstats
```

### Performance Investigation
```
,commandstats 20
,cogstats
,performance
```

### Post-Update Verification
```
,health
,test.sh (external)
,cogstats
```

## Technical Details

### Performance Impact
- Minimal overhead (< 1% CPU)
- Memory usage: ~10MB for metrics
- No blocking operations
- Async event handling

### Metric Accuracy
- Command times: Microsecond precision
- Resource monitoring: 5-minute intervals
- Error tracking: Real-time
- Counts: Exact

## Future Enhancements

1. **Persistent Metrics**: Database storage
2. **Visualization**: Web dashboard
3. **Alerts**: Discord/email notifications
4. **ML Analysis**: Anomaly detection
5. **Distributed**: Multi-instance support