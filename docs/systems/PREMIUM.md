# 💎 GOLEM Premium System

## Overview

The Premium system provides a role-based membership structure with exclusive benefits and features. It's designed to support server monetization while offering meaningful perks to supporters.

## Premium Tiers

Based on zgdk configuration, GOLEM supports multiple premium tiers:

### 🎫 zG50 - Git
- **Price**: 49 PLN ($14 USD)
- **Features**:
  - Custom color access via commands
  - Access to Git voice channel
  - Emoji/sticker access from all servers
  - 50% more activity points
  - 1 voice channel moderator slot

### 🎫 zG100 - Git Plus  
- **Price**: 99 PLN ($29 USD)
- **Features**:
  - Role at top of server
  - Team channel for 15 members
  - Git Plus voice channel creation
  - 2 voice moderator slots
  - 100% more activity points
  - All Git features included

### 🎫 zG500 - Git Pro
- **Price**: 499 PLN ($149 USD)
- **Features**:
  - Role above top members
  - Git Pro voice channel
  - Team up to 30 members
  - 3 voice moderators
  - Team color for all members
  - 200% more activity points
  - Auto-kick 1 person per channel

### 🎫 zG1000 - Git Ultra
- **Price**: 999 PLN ($299 USD)  
- **Features**:
  - Moderator permissions
  - Git Ultra voice channel
  - Team up to 50 members
  - 6 voice moderators
  - Monthly custom emoji addition
  - Team emoji badge
  - 300% more activity points
  - Auto-kick 3 people per channel

## Commands

### User Commands

#### 💎 View Premium Tiers
```
,premium
,vip
```
- Shows all available premium roles
- Lists features for each tier
- Displays prices in PLN and USD
- Includes donation link if configured

#### 🏅 Check Premium Status
```
,mypremium [@user]
,myrank [@user]
```
- Shows current premium roles
- Lists active benefits
- Displays role thumbnail
- Check others' premium status

#### 👥 Team Management
```
,team
,druzyna
```
- **Requires**: Premium role with team feature
- Shows team management options
- Displays team size limits
- Lists team commands (future)

### Admin Commands

#### ✅ Grant Premium
```
,givepremium @user <role_name>
```
- **Requires**: Administrator permission
- Assigns premium role to user
- Validates role exists and is premium
- Sends confirmation

#### ❌ Remove Premium
```
,removepremium @user <role_name>
```
- **Requires**: Administrator permission
- Removes premium role from user
- Sends confirmation

## Technical Implementation

### Configuration Loading
```python
def get_premium_config(self) -> List[Dict]:
    if self.bot.config:
        return self.bot.config.get_premium_roles()
    return []
```

### Premium Detection
```python
def has_premium(self, member: discord.Member) -> bool:
    premium_role_names = self.bot.config.get_premium_role_names()
    for role in member.roles:
        if role.name in premium_role_names:
            return True
    return False
```

### Role Structure
Premium roles are identified by name from config.yml:
```yaml
premium_roles:
  - name: "zG50"
    premium: "Git"
    price: 49
    features: [...]
```

## Benefits Integration

### Activity System
Premium multipliers applied automatically:
- zG50: 1.5x points (50% bonus)
- zG100: 2x points (100% bonus)
- zG500: 3x points (200% bonus)
- zG1000: 4x points (300% bonus)

### Voice Channels
Premium features for voice:
- Dedicated creation channels
- Moderator slots
- Auto-kick capabilities
- Extended permissions

### Teams (Future)
Team system allows:
- Shared team channel
- Team role with color
- Member management
- Activity sharing

## Configuration

From config.yml:
```yaml
premium_roles:
  - name: "zG50"
    premium: "Git"
    usd: 14
    price: 49
    features: [...]
    team_size: 0
    moderator_count: 1
    points_multiplier: 50
```

Key configuration fields:
- `name`: Role name in Discord
- `premium`: Display name
- `price`: PLN price
- `usd`: USD price
- `features`: List of benefits
- `team_size`: Max team members
- `moderator_count`: Voice mod slots
- `points_multiplier`: Activity bonus %

## Future Enhancements

### Planned Features
1. **Subscription Tracking**: Expiry dates
2. **Auto-Role Assignment**: Payment integration
3. **Team Channels**: Auto-create team areas
4. **Premium Commands**: Exclusive commands
5. **Statistics**: Premium user analytics

### Integration Ideas
- **Economy**: Premium-only shop items
- **Moderation**: Extended timeout limits
- **Voice**: Priority speaker in events
- **Custom**: Personal bot commands

## Best Practices

### For Users
- Check benefits with `,mypremium`
- Use team features if available
- Take advantage of point multipliers

### For Admins
- Keep roles properly configured
- Monitor premium role assignments
- Update benefits regularly
- Communicate changes clearly

## Bypass System (T)

The zgdk configuration includes a bypass system:
```yaml
bypass:
  duration:
    bump: 12
    activity: 6
```

This allows temporary premium-like benefits for:
- Server bumping
- High activity
- Special events

## Monetization

### Payment Methods
- Direct donation (configured URL)
- Payment verification system
- Manual role assignment
- Future: Auto-payment integration

### Pricing Strategy
- Tiered benefits
- Clear value progression
- Team discounts implicit
- Regional pricing considered