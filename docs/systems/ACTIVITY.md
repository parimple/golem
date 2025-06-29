# 📊 GOLEM Activity & Leveling System

## Overview

The Activity system tracks user engagement through messages and voice chat participation, converting activity into points and levels. It's designed to reward consistent participation while preventing spam.

## Core Concepts

### Points System
- **Message Points**: 10 base points per message
- **Long Message Bonus**: +5 points for messages >100 characters
- **Voice Points**: 5 points per minute in voice channels
- **Cooldown**: 60-second cooldown between message points

### Level Calculation
```python
level = int((points / 100) ** 0.5)
points_for_level = level ** 2 * 100
```
- Non-linear progression (quadratic)
- Level 1 = 100 points
- Level 10 = 10,000 points
- Level 20 = 40,000 points

## Commands

### User Commands

#### 📈 Level Check
```
,level [@user]
,lvl [@user]
,rank [@user]
```
- Shows current level and points
- Displays progress to next level
- Visual progress bar
- Shows user's avatar

#### 🏆 Leaderboard
```
,leaderboard [page]
,lb [page]
,top [page]
```
- Paginated leaderboard (10 per page)
- Shows level and total points
- Special emojis for top 3
- Navigation between pages

### Admin Commands

#### ✨ Add Points
```
,addpoints @user <points>
```
- **Requires**: Administrator permission
- Add points to any user
- Can trigger level up
- Shows if user leveled up

## Activity Tracking

### Message Activity
```python
@commands.Cog.listener()
async def on_message(self, message: discord.Message):
    # Award points for messages with cooldown
```
- Ignores bot messages
- Requires guild context
- 60-second cooldown per user
- Bonus for longer messages

### Voice Activity
```python
@tasks.loop(minutes=1)
async def voice_activity_tracker(self):
    # Award points for voice activity
```
- Runs every minute
- Ignores AFK channels
- Awards 5 points per minute
- No cooldown for voice

### Level Up Notifications
- Automatic announcement in channel
- Gold-colored embed
- Self-deleting after 10 seconds
- Shows new level achieved

## Technical Implementation

### Storage
```python
class ActivityCog:
    def __init__(self, bot):
        self.user_points = {}      # user_id: points
        self.user_levels = {}      # user_id: level
        self.last_message = {}     # user_id: datetime
```

### Point Management
```python
def add_points(self, user_id: int, points: int) -> tuple[int, bool]:
    # Returns (new_total, leveled_up)
```
- Calculates old and new levels
- Detects level ups
- Updates both points and levels

## Configuration

Current hardcoded values:
```python
self.message_points = 10
self.voice_points_per_minute = 5
self.cooldown_seconds = 60
```

Future config.yml integration:
```yaml
activity:
  message_points: 10
  message_length_bonus: 5
  voice_points_per_minute: 5
  cooldown_seconds: 60
  announce_levelup: true
```

## Level Rewards (Future)

### Planned Integrations
1. **Role Rewards**: Auto-assign roles at levels
2. **Permission Unlocks**: Access to channels/commands
3. **Economy Bonuses**: G rewards for leveling
4. **Premium Multipliers**: 2x points for premium

### Example Role Structure
- Level 5: Active Member
- Level 10: Regular
- Level 20: Veteran
- Level 50: Legend

## Best Practices

### For Users
- Engage naturally in conversations
- Join voice channels for passive points
- Avoid spamming (cooldown prevents abuse)

### For Admins
- Monitor for unusual activity patterns
- Adjust point values for balance
- Consider reset events

## Statistics

### Current Implementation
- Total points tracking
- Level distribution
- Activity patterns

### Future Analytics
- Daily/weekly activity graphs
- Most active hours
- Channel-specific activity
- Voice vs text activity ratio

## Anti-Abuse Measures

### Current
- 60-second message cooldown
- Bot message filtering
- Guild-only tracking

### Planned
- Spam detection
- AFK detection in voice
- Diminishing returns
- Activity caps

## Integration with Other Systems

### Economy
- Points could convert to G
- Level-based daily bonuses
- Shop discounts by level

### Premium
- Point multipliers for premium
- Exclusive level rewards
- Faster progression

### Moderation
- Activity requirements for roles
- Timeout affects point gain
- Good behavior bonuses