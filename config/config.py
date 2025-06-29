"""
GOLEM Configuration System
Handles configuration loading from zgdk-style config.yml
"""
import yaml
import os
from typing import Dict, Any, List, Optional
from pathlib import Path


class Config:
    """Configuration manager for GOLEM"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config.yml"
        self.data = {}
        self.load()
    
    def load(self):
        """Load configuration from file"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.data = yaml.safe_load(f) or {}
        else:
            # Use default configuration
            self.data = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'prefix': ',',
            'description': 'GOLEM - The Ultimate Discord Bot',
            'guild_id': None,
            
            # Emoji configuration
            'emojis': {},
            
            # Channel configuration
            'channels': {},
            'channels_voice': {},
            'channels_create': [],
            'vc_categories': [],
            
            # Role configuration
            'roles': {
                'premium': [],
                'boosters': [],
            },
            
            # Premium roles configuration
            'premium_roles': [],
            
            # Voice permissions
            'voice_permissions': {
                'boosters': [],
                'commands': {},
                'bypass': {
                    'duration': {
                        'bump': 12,
                        'activity': 6,
                    }
                }
            },
            
            # Mute roles
            'mute_roles': [],
            
            # Color and team configuration
            'color': {
                'role_name': '✎',
                'base_role_id': None,
            },
            'team': {
                'symbol': '☫',
                'base_role_id': None,
                'category_id': None,
            },
            
            # Activity ranks
            'activity_ranks': {
                'enabled': True,
                'default_count': 2,
                'max_count': 99,
                'default_ranks': [
                    {
                        'name': '1',
                        'points_required': 1000,
                        'color': '#FFD700',
                    },
                    {
                        'name': '2',
                        'points_required': 5000,
                        'color': '#FF69B4',
                    }
                ],
                'premium_customization': {
                    'enabled': True,
                    'required_role': 'zG500',
                }
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key"""
        keys = key.split('.')
        value = self.data
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value if value is not None else default
    
    def set(self, key: str, value: Any):
        """Set configuration value by dot-notation key"""
        keys = key.split('.')
        target = self.data
        
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        
        target[keys[-1]] = value
    
    def save(self):
        """Save configuration to file"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.data, f, allow_unicode=True, default_flow_style=False)
    
    @property
    def prefix(self) -> str:
        """Get command prefix"""
        return self.get('prefix', ',')
    
    @property
    def guild_id(self) -> Optional[int]:
        """Get guild ID"""
        return self.get('guild_id')
    
    @property
    def owner_ids(self) -> List[int]:
        """Get owner IDs"""
        ids = self.get('owner_ids', [])
        # Also include legacy owner_id if present
        legacy_id = self.get('owner_id')
        if legacy_id and legacy_id not in ids:
            ids.append(legacy_id)
        return ids
    
    def get_channel(self, name: str) -> Optional[int]:
        """Get channel ID by name"""
        return self.get(f'channels.{name}')
    
    def get_emoji(self, name: str) -> str:
        """Get emoji by name"""
        return self.get(f'emojis.{name}', '')
    
    def get_premium_roles(self) -> List[Dict[str, Any]]:
        """Get premium role configurations"""
        return self.get('premium_roles', [])
    
    def get_premium_role_names(self) -> List[str]:
        """Get list of premium role names"""
        return [role['name'] for role in self.get_premium_roles()]
    
    def get_mute_roles(self) -> List[Dict[str, Any]]:
        """Get mute role configurations"""
        return self.get('mute_roles', [])
    
    def get_voice_command_config(self, command: str) -> Dict[str, Any]:
        """Get voice command configuration"""
        return self.get(f'voice_commands.{command}', {})
    
    def get_bypass_duration(self, action: str) -> int:
        """Get bypass duration for action"""
        return self.get(f'voice_permissions.bypass.duration.{action}', 0)
    
    def get_activity_ranks_config(self) -> Dict[str, Any]:
        """Get activity ranks configuration"""
        return self.get('activity_ranks', {})
    
    def is_owner(self, user_id: int) -> bool:
        """Check if user is bot owner"""
        return user_id in self.owner_ids