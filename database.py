"""
Database operations for Telegram RPG Bot
Supports both SQLite (development) and PostgreSQL (production)
"""

import sqlite3
import asyncio
import logging
import os
import aiosqlite
from typing import Optional, Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.db_path = os.getenv('DATABASE_PATH', 'rpg_bot.db')
        self.use_sqlite = True  # Switch to PostgreSQL in production

    async def init_database(self):
        """Initialize database tables"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Players table
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS players (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT NOT NULL,
                        element TEXT NOT NULL,
                        level INTEGER DEFAULT 1,
                        experience INTEGER DEFAULT 0,
                        hp INTEGER DEFAULT 100,
                        max_hp INTEGER DEFAULT 100,
                        stamina INTEGER DEFAULT 50,
                        max_stamina INTEGER DEFAULT 50,
                        attack INTEGER DEFAULT 25,
                        defense INTEGER DEFAULT 20,
                        agility INTEGER DEFAULT 15,
                        element_power INTEGER DEFAULT 30,
                        coins INTEGER DEFAULT 100,
                        battles_won INTEGER DEFAULT 0,
                        battles_lost INTEGER DEFAULT 0,
                        last_daily_claim TEXT,
                        daily_streak INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Inventory table
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS inventory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        item_id TEXT NOT NULL,
                        quantity INTEGER DEFAULT 1,
                        equipped BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES players (user_id)
                    )
                ''')

                # Battle history table
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS battle_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        battle_type TEXT NOT NULL,
                        player1_id INTEGER NOT NULL,
                        player2_id INTEGER,
                        winner_id INTEGER,
                        battle_data TEXT,
                        rewards TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (player1_id) REFERENCES players (user_id),
                        FOREIGN KEY (player2_id) REFERENCES players (user_id),
                        FOREIGN KEY (winner_id) REFERENCES players (user_id)
                    )
                ''')

                # Achievements table
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS achievements (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        achievement_id TEXT NOT NULL,
                        unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES players (user_id)
                    )
                ''')

                await db.commit()
                logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    async def create_player(self, user_id: int, username: str, element: str) -> bool:
        """Create a new player"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO players (user_id, username, element)
                    VALUES (?, ?, ?)
                ''', (user_id, username, element))

                await db.commit()
                logger.info(f"Created new player: {username} ({user_id}) - Element: {element}")
                return True

        except sqlite3.IntegrityError:
            logger.warning(f"Player {user_id} already exists")
            return False
        except Exception as e:
            logger.error(f"Error creating player: {e}")
            return False

    async def get_player(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get player data by user ID"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute('''
                    SELECT * FROM players WHERE user_id = ?
                ''', (user_id,)) as cursor:
                    row = await cursor.fetchone()

                    if row:
                        return dict(row)
                    return None

        except Exception as e:
            logger.error(f"Error getting player {user_id}: {e}")
            return None

    async def update_player_stats(self, user_id: int, stats: Dict[str, Any]) -> bool:
        """Update player statistics"""
        if not stats:
return True

        try:
            # Add updated_at timestamp
            stats['updated_at'] = datetime.now().isoformat()

            # Build dynamic update query
            set_clause = ', '.join([f"{key} = ?" for key in stats.keys()])
            values = list(stats.values()) + [user_id]

            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(f'''
                    UPDATE players 
                    SET {set_clause}
                    WHERE user_id = ?
                ''', values)

                await db.commit()
                return True

        except Exception as e:
            logger.error(f"Error updating player stats for {user_id}: {e}")
            return False

    async def increase_player_stats(self, user_id: int, stat_increases: Dict[str, int]) -> bool:
        """Increase player stats by specified amounts"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # First get current stats
                db.row_factory = aiosqlite.Row
                async with db.execute('SELECT * FROM players WHERE user_id = ?', (user_id,)) as cursor:
                    player = await cursor.fetchone()

                if not player:
                    return False

                # Calculate new values
                updates = {'updated_at': datetime.now().isoformat()}
                for stat, increase in stat_increases.items():
                    if stat in dict(player):
                        current_value = player[stat] if player[stat] is not None else 0
                        updates[stat] = current_value + increase

                # Update database
                if updates:
                    set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
                    values = list(updates.values()) + [user_id]

                    await db.execute(f'''
                        UPDATE players 
                        SET {set_clause}
                        WHERE user_id = ?
                    ''', values)

                    await db.commit()
                    return True

        except Exception as e:
            logger.error(f"Error increasing player stats for {user_id}: {e}")
            return False

    async def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all registered users"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute('SELECT * FROM players ORDER BY created_at DESC') as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []

    async def get_top_players(self, limit: int = 10, order_by: str = 'level') -> List[Dict[str, Any]]:
        """Get top players by specified criteria"""
        try:
            valid_orders = ['level', 'experience', 'battles_won', 'coins']
            if order_by not in valid_orders:
                order_by = 'level'

            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row

                # Order by level first, then experience as tiebreaker
                query = f'''
                    SELECT * FROM players 
                    ORDER BY {order_by} DESC, experience DESC 
                    LIMIT ?
                '''

                async with db.execute(query, (limit,)) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Error getting top players: {e}")
            return []

    async def log_battle(self, battle_type: str, player1_id: int, player2_id: Optional[int], 
                        winner_id: int, battle_data: Dict, rewards: Dict) -> bool:
        """Log battle history"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO battle_history 
                    (battle_type, player1_id, player2_id, winner_id, battle_data, rewards)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    battle_type, 
                    player1_id, 
                    player2_id, 
                    winner_id,
                    str(battle_data),  # Convert dict to string
                    str(rewards)
                ))

                await db.commit()
                return True

        except Exception as e:
            logger.error(f"Error logging battle: {e}")
            return False
