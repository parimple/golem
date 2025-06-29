# 💰 GOLEM Economy System

## Overview

The Economy system in GOLEM provides a virtual currency system that allows users to earn, spend, and transfer currency (called "G"). It's designed to be simple yet engaging, with room for expansion.

## Core Concepts

### Currency: "G"
- The base currency unit
- Non-fractional (integer values only)
- No maximum limit
- Stored in-memory (persists until bot restart)

### Balance Management
Each user has a wallet that tracks their G balance. The system ensures:
- Balances cannot go negative
- Transfers are atomic (all-or-nothing)
- Admin overrides are logged

## Commands

### User Commands

#### 💵 Balance Check
```
,balance [@user]
,bal [@user]
,wallet [@user]
,portfel [@user]
```
- Check your or another user's balance
- Shows formatted balance with thousands separators
- Displays in an embed with gold color

#### 📅 Daily Reward
```
,daily
,dzienny
```
- Claim 100 G once per day
- No cooldown system yet (can be claimed multiple times)
- Shows new balance after claiming

#### 💸 Transfer Money
```
,pay @user <amount>
,transfer @user <amount>
,send @user <amount>
```
- Transfer G to another user
- Validates sufficient balance
- Amount must be positive
- Instant transfer with confirmation

#### 💎 Rich List
```
,richest
,rich
,balancetop
```
- Shows top 10 richest users
- Sorted by balance descending
- Displays with user mentions and formatted amounts

### Admin Commands

#### 💵 Add Money
```
,addmoney @user <amount>
,addbal @user <amount>
```
- **Requires**: Administrator permission
- Add any amount of G to a user
- Can be negative to remove money
- Shows new balance after operation

## Technical Implementation

### Storage
```python
class EconomyCog:
    def __init__(self, bot):
        self.balances = {}  # user_id: balance
```
- Simple dictionary storage
- No persistence between restarts
- Ready for database migration

### Balance Operations
```python
def get_balance(self, user_id: int) -> int:
    return self.balances.get(user_id, 0)

def add_balance(self, user_id: int, amount: int) -> int:
    current = self.get_balance(user_id)
    self.balances[user_id] = current + amount
    return self.balances[user_id]
```

## Future Enhancements

### Planned Features
1. **Persistence**: SQLite/PostgreSQL storage
2. **Daily Cooldowns**: 24-hour cooldown for daily rewards
3. **Interest System**: Passive income based on balance
4. **Gambling Commands**: Coinflip betting, slots
5. **Shop Integration**: Buy roles, colors, perks

### Integration Points
- **Premium System**: Premium roles could give bonus daily rewards
- **Activity System**: Earn G for activity points
- **Moderation**: Fine system for rule violations

## Configuration

Currently hardcoded values:
```python
daily_reward = 100  # G per daily claim
```

Future config.yml integration:
```yaml
economy:
  daily_reward: 100
  starting_balance: 0
  max_transfer: 1000000
  currency_name: "G"
  currency_symbol: "💰"
```

## Best Practices

### For Users
- Check balance before transfers
- Use daily command every day
- Be careful with large transfers

### For Admins
- Use addmoney sparingly
- Consider economy balance when adding
- Monitor for inflation

## Error Handling

The system handles:
- ❌ Insufficient balance
- ❌ Invalid amounts (negative, zero)
- ❌ Self-transfers (not explicitly blocked yet)
- ❌ Missing permissions

All errors display user-friendly messages with clear explanations.