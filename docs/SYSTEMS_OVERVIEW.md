# 🧬 GOLEM Systems Documentation

## Overview

GOLEM integrates multiple interconnected systems that work together to create a comprehensive Discord bot experience. Each system is designed with simplicity and extensibility in mind.

## Core Systems

### 💰 [Economy System](systems/ECONOMY.md)
Virtual currency system with:
- Wallet management
- Daily rewards
- Transfer capabilities
- Admin controls
- Rich user leaderboard

### 📊 [Activity & Leveling System](systems/ACTIVITY.md)
Engagement tracking with:
- Message and voice activity points
- Level progression
- Activity leaderboard
- Level-up notifications
- Anti-spam measures

### 💎 [Premium System](systems/PREMIUM.md)
Role-based membership with:
- Multiple tier support
- Team management
- Activity multipliers
- Exclusive features
- Configuration-driven

### 🔧 [Performance Monitoring](systems/MONITORING.md)
Real-time performance tracking:
- Command execution metrics
- Cog health monitoring
- System resource tracking
- Error rate analysis
- Health check commands

## System Integration

### Economy ↔️ Activity
- Future: Convert activity points to currency
- Level-based bonuses for economy
- Premium multipliers affect both

### Premium ↔️ Activity
- Premium roles get point multipliers
- Higher tiers = more benefits
- Team features for premium users

### Monitoring ↔️ All Systems
- Tracks performance across all cogs
- Identifies bottlenecks
- Monitors resource usage
- Health checks for each system

## Configuration

All systems respect the main `config.yml`:
```yaml
# Economy settings
economy:
  daily_reward: 100
  currency_name: "G"

# Activity settings  
activity:
  message_points: 10
  voice_points_per_minute: 5

# Premium roles
premium_roles:
  - name: "zG50"
    price: 49
    features: [...]

# Monitoring thresholds
monitoring:
  memory_warning: 500  # MB
  cpu_warning: 80      # %
```

## Data Storage

### Current Implementation
- In-memory storage for all systems
- No persistence between restarts
- Fast and simple
- Ready for database migration

### Future Migration
```python
# Easy to migrate to database
class EconomyRepository:
    async def get_balance(self, user_id: int) -> int
    async def update_balance(self, user_id: int, amount: int)
```

## Testing

### Integration Tests
```bash
# Run all tests
./test.sh

# Specific system tests
python tests/test_cog_loading.py
```

### Manual Testing
1. Load bot with all systems
2. Run `,health` for system check
3. Test each system's commands
4. Monitor with `,performance`

## Best Practices

### For Developers
1. Keep systems loosely coupled
2. Use configuration over hardcoding
3. Plan for database migration
4. Add monitoring hooks
5. Write tests for new features

### For Administrators
1. Regular health checks
2. Monitor performance metrics
3. Adjust configurations as needed
4. Watch for system interactions
5. Plan capacity for growth

## Scaling Considerations

### Current Limits
- Memory: In-memory storage limits
- Users: Tested up to 10k users
- Commands: 100+ commands/second
- Guilds: Optimized for 100+ servers

### Optimization Tips
1. Enable only needed systems
2. Adjust monitoring intervals
3. Configure reasonable limits
4. Use caching where possible
5. Monitor resource usage

## Future Roadmap

### Phase 1: Database Integration
- PostgreSQL support
- Data persistence
- Migration tools

### Phase 2: Advanced Features
- Web dashboard
- API endpoints
- Webhook integrations
- Advanced analytics

### Phase 3: AI Integration
- Predictive systems
- Automated optimization
- Smart recommendations
- Natural language commands

## Support

### Documentation
- System-specific docs in `docs/systems/`
- Code comments for implementation
- Example configurations

### Monitoring
- Use `,help` for command list
- Check `,health` for status
- Review `,performance` for metrics
- See logs for detailed info