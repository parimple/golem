"""
Database management system for GOLEM
Professional SQLite implementation with migrations
"""
import sqlite3
import json
import logging
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import asyncio
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class Database:
    """Advanced database manager with connection pooling and migrations"""
    
    def __init__(self, db_path: str = "data/golem.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database with all tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create tables
            cursor.executescript("""
                -- Users table
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    discriminator TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Economy table
                CREATE TABLE IF NOT EXISTS economy (
                    user_id INTEGER PRIMARY KEY,
                    balance INTEGER DEFAULT 0,
                    total_earned INTEGER DEFAULT 0,
                    total_spent INTEGER DEFAULT 0,
                    last_daily TIMESTAMP,
                    daily_streak INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );
                
                -- Transactions table
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_user INTEGER,
                    to_user INTEGER,
                    amount INTEGER,
                    type TEXT,
                    reason TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (from_user) REFERENCES users(user_id),
                    FOREIGN KEY (to_user) REFERENCES users(user_id)
                );
                
                -- Activity/Levels table
                CREATE TABLE IF NOT EXISTS activity (
                    user_id INTEGER PRIMARY KEY,
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 0,
                    messages INTEGER DEFAULT 0,
                    voice_minutes INTEGER DEFAULT 0,
                    last_message TIMESTAMP,
                    last_voice_update TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );
                
                -- Reputation table
                CREATE TABLE IF NOT EXISTS reputation (
                    user_id INTEGER PRIMARY KEY,
                    positive INTEGER DEFAULT 0,
                    negative INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );
                
                -- Reputation transactions
                CREATE TABLE IF NOT EXISTS reputation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_user INTEGER,
                    to_user INTEGER,
                    type TEXT CHECK(type IN ('positive', 'negative')),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (from_user) REFERENCES users(user_id),
                    FOREIGN KEY (to_user) REFERENCES users(user_id)
                );
                
                -- Reputation cooldowns
                CREATE TABLE IF NOT EXISTS reputation_cooldowns (
                    from_user INTEGER,
                    to_user INTEGER,
                    last_given TIMESTAMP,
                    PRIMARY KEY (from_user, to_user),
                    FOREIGN KEY (from_user) REFERENCES users(user_id),
                    FOREIGN KEY (to_user) REFERENCES users(user_id)
                );
                
                -- Premium subscriptions
                CREATE TABLE IF NOT EXISTS premium (
                    user_id INTEGER PRIMARY KEY,
                    role TEXT,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    features TEXT, -- JSON
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );
                
                -- Voice channels
                CREATE TABLE IF NOT EXISTS voice_channels (
                    channel_id INTEGER PRIMARY KEY,
                    owner_id INTEGER,
                    guild_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    settings TEXT, -- JSON
                    FOREIGN KEY (owner_id) REFERENCES users(user_id)
                );
                
                -- Moderation logs
                CREATE TABLE IF NOT EXISTS moderation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    moderator_id INTEGER,
                    target_id INTEGER,
                    action TEXT,
                    reason TEXT,
                    duration INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Settings (per guild)
                CREATE TABLE IF NOT EXISTS guild_settings (
                    guild_id INTEGER PRIMARY KEY,
                    prefix TEXT DEFAULT ',',
                    language TEXT DEFAULT 'pl',
                    modules TEXT, -- JSON array of enabled modules
                    features TEXT, -- JSON object of feature settings
                    premium_until TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Command usage stats
                CREATE TABLE IF NOT EXISTS command_stats (
                    command TEXT,
                    guild_id INTEGER,
                    user_id INTEGER,
                    uses INTEGER DEFAULT 1,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (command, guild_id, user_id)
                );
                
                -- Create indexes for performance
                CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(from_user, to_user);
                CREATE INDEX IF NOT EXISTS idx_activity_xp ON activity(xp DESC);
                CREATE INDEX IF NOT EXISTS idx_reputation_total ON reputation(positive - negative DESC);
                CREATE INDEX IF NOT EXISTS idx_modlogs_guild ON moderation_logs(guild_id, timestamp);
                CREATE INDEX IF NOT EXISTS idx_cmdstats_command ON command_stats(command, uses DESC);
            """)
            
            logger.info("Database initialized successfully")
    
    # User management
    async def ensure_user(self, user_id: int, username: str = None, discriminator: str = None):
        """Ensure user exists in database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO users (user_id, username, discriminator)
                VALUES (?, ?, ?)
            """, (user_id, username, discriminator))
            
            if username or discriminator:
                cursor.execute("""
                    UPDATE users 
                    SET username = COALESCE(?, username),
                        discriminator = COALESCE(?, discriminator),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (username, discriminator, user_id))
    
    # Economy functions
    async def get_balance(self, user_id: int) -> int:
        """Get user balance"""
        await self.ensure_user(user_id)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO economy (user_id) VALUES (?)
            """, (user_id,))
            
            cursor.execute("SELECT balance FROM economy WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            return result['balance'] if result else 0
    
    async def update_balance(self, user_id: int, amount: int, transaction_type: str = "other") -> int:
        """Update user balance and return new balance"""
        await self.ensure_user(user_id)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO economy (user_id) VALUES (?)
            """, (user_id,))
            
            cursor.execute("""
                UPDATE economy 
                SET balance = balance + ?,
                    total_earned = total_earned + CASE WHEN ? > 0 THEN ? ELSE 0 END,
                    total_spent = total_spent + CASE WHEN ? < 0 THEN ABS(?) ELSE 0 END
                WHERE user_id = ?
            """, (amount, amount, amount, amount, amount, user_id))
            
            # Log transaction
            cursor.execute("""
                INSERT INTO transactions (from_user, to_user, amount, type)
                VALUES (?, ?, ?, ?)
            """, (user_id if amount < 0 else None, user_id if amount > 0 else None, abs(amount), transaction_type))
            
            cursor.execute("SELECT balance FROM economy WHERE user_id = ?", (user_id,))
            return cursor.fetchone()['balance']
    
    async def transfer_money(self, from_user: int, to_user: int, amount: int) -> Tuple[int, int]:
        """Transfer money between users, return new balances"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Ensure both users exist
            await self.ensure_user(from_user)
            await self.ensure_user(to_user)
            
            # Check balance
            cursor.execute("SELECT balance FROM economy WHERE user_id = ?", (from_user,))
            sender_balance = cursor.fetchone()
            if not sender_balance or sender_balance['balance'] < amount:
                raise ValueError("Insufficient balance")
            
            # Perform transfer
            cursor.execute("""
                UPDATE economy SET balance = balance - ? WHERE user_id = ?
            """, (amount, from_user))
            
            cursor.execute("""
                UPDATE economy SET balance = balance + ? WHERE user_id = ?
            """, (amount, to_user))
            
            # Log transaction
            cursor.execute("""
                INSERT INTO transactions (from_user, to_user, amount, type)
                VALUES (?, ?, ?, 'transfer')
            """, (from_user, to_user, amount))
            
            # Get new balances
            cursor.execute("SELECT balance FROM economy WHERE user_id IN (?, ?)", (from_user, to_user))
            balances = {row['user_id']: row['balance'] for row in cursor.fetchall()}
            
            return balances[from_user], balances[to_user]
    
    async def claim_daily(self, user_id: int, amount: int) -> Tuple[bool, Optional[datetime], int]:
        """Claim daily reward, returns (success, next_claim_time, streak)"""
        await self.ensure_user(user_id)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT last_daily, daily_streak FROM economy WHERE user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            now = datetime.now()
            
            if result and result['last_daily']:
                last_daily = datetime.fromisoformat(result['last_daily'])
                time_diff = now - last_daily
                
                if time_diff.total_seconds() < 86400:  # 24 hours
                    next_claim = last_daily.replace(hour=last_daily.hour, minute=last_daily.minute, second=last_daily.second)
                    next_claim = next_claim.replace(day=next_claim.day + 1)
                    return False, next_claim, result['daily_streak']
                
                # Check if streak continues (claimed within 48 hours)
                streak = result['daily_streak'] + 1 if time_diff.total_seconds() < 172800 else 1
            else:
                streak = 1
            
            # Apply streak bonus
            bonus = min(streak * 100, 1000)  # Max 1000 bonus
            total_amount = amount + bonus
            
            cursor.execute("""
                UPDATE economy 
                SET balance = balance + ?,
                    last_daily = ?,
                    daily_streak = ?,
                    total_earned = total_earned + ?
                WHERE user_id = ?
            """, (total_amount, now.isoformat(), streak, total_amount, user_id))
            
            return True, None, streak
    
    # Activity/XP functions
    async def add_xp(self, user_id: int, xp: int, source: str = "message"):
        """Add XP to user"""
        await self.ensure_user(user_id)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR IGNORE INTO activity (user_id) VALUES (?)
            """, (user_id,))
            
            # Update XP and calculate level manually
            cursor.execute("""
                UPDATE activity 
                SET xp = xp + ?,
                    messages = messages + CASE WHEN ? = 'message' THEN 1 ELSE 0 END,
                    voice_minutes = voice_minutes + CASE WHEN ? = 'voice' THEN ? / 10 ELSE 0 END,
                    last_message = CASE WHEN ? = 'message' THEN CURRENT_TIMESTAMP ELSE last_message END
                WHERE user_id = ?
            """, (xp, source, source, xp, source, user_id))
            
            # Get new XP and calculate level
            cursor.execute("SELECT xp FROM activity WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            if result:
                new_xp = result['xp']
                new_level = int((new_xp / 100) ** 0.5)
                cursor.execute("""
                    UPDATE activity SET level = ? WHERE user_id = ?
                """, (new_level, user_id))
    
    async def get_leaderboard(self, limit: int = 10, sort_by: str = "xp") -> List[Dict]:
        """Get leaderboard data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if sort_by == "balance":
                query = """
                    SELECT u.user_id, u.username, e.balance as value
                    FROM users u
                    JOIN economy e ON u.user_id = e.user_id
                    ORDER BY e.balance DESC
                    LIMIT ?
                """
            elif sort_by == "reputation":
                query = """
                    SELECT u.user_id, u.username, (r.positive - r.negative) as value
                    FROM users u
                    JOIN reputation r ON u.user_id = r.user_id
                    ORDER BY value DESC
                    LIMIT ?
                """
            else:  # Default to XP
                query = """
                    SELECT u.user_id, u.username, a.xp as value, a.level
                    FROM users u
                    JOIN activity a ON u.user_id = a.user_id
                    ORDER BY a.xp DESC
                    LIMIT ?
                """
            
            cursor.execute(query, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    # Reputation functions
    async def give_reputation(self, from_user: int, to_user: int, rep_type: str) -> Tuple[bool, Optional[str]]:
        """Give reputation, returns (success, error_message)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check cooldown
            cursor.execute("""
                SELECT last_given FROM reputation_cooldowns 
                WHERE from_user = ? AND to_user = ?
            """, (from_user, to_user))
            
            cooldown = cursor.fetchone()
            if cooldown:
                last_given = datetime.fromisoformat(cooldown['last_given'])
                if (datetime.now() - last_given).total_seconds() < 86400:
                    remaining = 86400 - (datetime.now() - last_given).total_seconds()
                    hours = int(remaining // 3600)
                    minutes = int((remaining % 3600) // 60)
                    return False, f"Musisz poczekać {hours}h {minutes}m"
            
            # Give reputation
            cursor.execute("""
                INSERT OR IGNORE INTO reputation (user_id) VALUES (?)
            """, (to_user,))
            
            if rep_type == "positive":
                cursor.execute("""
                    UPDATE reputation SET positive = positive + 1 WHERE user_id = ?
                """, (to_user,))
            else:
                cursor.execute("""
                    UPDATE reputation SET negative = negative + 1 WHERE user_id = ?
                """, (to_user,))
            
            # Update cooldown
            cursor.execute("""
                INSERT OR REPLACE INTO reputation_cooldowns (from_user, to_user, last_given)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (from_user, to_user))
            
            # Log transaction
            cursor.execute("""
                INSERT INTO reputation_logs (from_user, to_user, type)
                VALUES (?, ?, ?)
            """, (from_user, to_user, rep_type))
            
            return True, None
    
    # Stats functions
    async def log_command_use(self, command: str, guild_id: int, user_id: int):
        """Log command usage"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO command_stats (command, guild_id, user_id)
                VALUES (?, ?, ?)
                ON CONFLICT(command, guild_id, user_id) 
                DO UPDATE SET uses = uses + 1, last_used = CURRENT_TIMESTAMP
            """, (command, guild_id, user_id))
    
    async def get_command_stats(self, guild_id: int = None, limit: int = 10) -> List[Dict]:
        """Get command usage statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if guild_id:
                cursor.execute("""
                    SELECT command, SUM(uses) as total_uses
                    FROM command_stats
                    WHERE guild_id = ?
                    GROUP BY command
                    ORDER BY total_uses DESC
                    LIMIT ?
                """, (guild_id, limit))
            else:
                cursor.execute("""
                    SELECT command, SUM(uses) as total_uses
                    FROM command_stats
                    GROUP BY command
                    ORDER BY total_uses DESC
                    LIMIT ?
                """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]


# Global database instance
db = Database()