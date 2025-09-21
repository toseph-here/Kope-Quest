"""
Configuration file for Telegram RPG Bot
Contains all game settings, balancing, and static data
"""

import os

class Config:
    """Game configuration constants"""

    # Bot settings
    BOT_TOKEN = os.getenv('BOT_TOKEN', '')
    OWNER_ID = int(os.getenv('OWNER_ID', 8094286612))
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')

    # Database settings
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'rpg_bot.db')

    # Game balance settings
    BASE_XP_FORMULA = 100  # Level² × 100 for XP requirements
    LEVEL_UP_STAT_INCREASE = 5
    MAX_LEVEL = 100

    # Combat settings
    BASE_CRIT_CHANCE = 0.1  # 10%
    CRIT_DAMAGE_MULTIPLIER = 1.5
    ELEMENT_SKILL_STAMINA_COST = 15
    HEAL_STAMINA_COST = 10

    # Element system
    ELEMENTS = {
        'Fire': {
            'emoji': '🔥',
            'description': 'Fierce and destructive',
            'strong_against': ['Ice', 'Earth'],
            'weak_against': ['Water'],
            'color': '#FF4500'
        },
        'Ice': {
            'emoji': '❄️',
            'description': 'Cold and controlling',
            'strong_against': ['Water', 'Earth'],
            'weak_against': ['Fire', 'Lightning'],
            'color': '#00BFFF'
        },
        'Lightning': {
            'emoji': '⚡',
            'description': 'Fast and shocking',
            'strong_against': ['Water', 'Wind'],
            'weak_against': ['Earth'],
            'color': '#FFD700'
        },
        'Water': {
            'emoji': '🌊',
            'description': 'Flowing and adaptable',
            'strong_against': ['Fire', 'Earth'],
            'weak_against': ['Lightning', 'Ice'],
            'color': '#1E90FF'
        },
        'Earth': {
            'emoji': '🌍',
            'description': 'Strong and enduring',
            'strong_against': ['Lightning', 'Fire'],
            'weak_against': ['Water', 'Wind'],
            'color': '#8B4513'
        },
        'Wind': {
            'emoji': '💨',
            'description': 'Swift and free',
            'strong_against': ['Earth', 'Shadow'],
            'weak_against': ['Lightning'],
            'color': '#87CEEB'
        },
        'Shadow': {
            'emoji': '🌙',
            'description': 'Mysterious and cunning',
            'strong_against': ['Light', 'Wind'],
            'weak_against': ['Light'],
            'color': '#4B0082'
        },
        'Light': {
            'emoji': '🌟',
            'description': 'Pure and healing',
            'strong_against': ['Shadow', 'Dark'],
            'weak_against': ['Shadow'],
            'color': '#FFD700'
        }
    }

    # Locations and their properties
    LOCATIONS = {
        'Burning Volcano': {
            'emoji': '🌋',
            'element': 'Fire',
            'min_level': 1,
            'max_level': 5,
            'enemy_types': ['Flame Sprite', 'Lava Golem', 'Fire Elemental'],
            'description': 'A dangerous volcanic region where fire creatures roam.',
            'base_xp_multiplier': 1.0,
            'base_coin_multiplier': 1.0
        },
        'Frozen Tundra': {
            'emoji': '🏔️',
            'element': 'Ice',
            'min_level': 3,
            'max_level': 8,
            'enemy_types': ['Frost Wolf', 'Ice Shard', 'Frozen Warrior'],
            'description': 'A freezing wasteland home to ice creatures.',
            'base_xp_multiplier': 1.1,
            'base_coin_multiplier': 1.1
        },
        'Storm Peaks': {
            'emoji': '⛈️',
            'element': 'Lightning',
            'min_level': 5,
            'max_level': 12,
            'enemy_types': ['Storm Eagle', 'Thunder Beast', 'Lightning Wisp'],
            'description': 'Mountain peaks constantly struck by lightning.',
            'base_xp_multiplier': 1.2,
            'base_coin_multiplier': 1.2
        },
        'Mystic Ocean': {
            'emoji': '🌊',
            'element': 'Water',
            'min_level': 4,
            'max_level': 10,
            'enemy_types': ['Water Nymph', 'Tide Guardian', 'Aqua Serpent'],
            'description': 'Deep ocean waters filled with aquatic creatures.',
            'base_xp_multiplier': 1.15,
            'base_coin_multiplier': 1.1
        },
        'Ancient Caverns': {
            'emoji': '🏔️',
            'element': 'Earth',
            'min_level': 6,
            'max_level': 15,
            'enemy_types': ['Stone Golem', 'Rock Crusher', 'Earth Shaker'],
            'description': 'Deep underground caves with earth elementals.',
            'base_xp_multiplier': 1.25,
            'base_coin_multiplier': 1.2
        },
        'Sky Gardens': {
            'emoji': '☁️',
            'element': 'Wind',
            'min_level': 8,
            'max_level': 18,
            'enemy_types': ['Wind Dancer', 'Gale Force', 'Sky Hunter'],
            'description': 'Floating gardens in the clouds.',
            'base_xp_multiplier': 1.3,
            'base_coin_multiplier': 1.25
        },
        'Dark Forest': {
            'emoji': '🌚',
            'element': 'Shadow',
            'min_level': 10,
            'max_level': 22,
            'enemy_types': ['Shadow Wraith', 'Dark Assassin', 'Void Stalker'],
            'description': 'A mysterious forest shrouded in darkness.',
            'base_xp_multiplier': 1.4,
            'base_coin_multiplier': 1.3
        },
        'Sacred Temple': {
            'emoji': '🏛️',
            'element': 'Light',
            'min_level': 12,
            'max_level': 25,
            'enemy_types': ['Light Guardian', 'Solar Warrior', 'Divine Beast'],
            'description': 'An ancient temple radiating pure light energy.',
            'base_xp_multiplier': 1.5,
            'base_coin_multiplier': 1.4
        }
    }

    # Shop items
    SHOP_ITEMS = {
        'health_potion': {
            'name': 'Health Potion',
            'emoji': '🧪',
            'type': 'consumable',
            'price': 25,
            'effects': {'heal': 30},
            'description': 'Restores 30 HP instantly'
        },
        'stamina_potion': {
            'name': 'Stamina Potion',
            'emoji': '⚗️',
            'type': 'consumable',
            'price': 20,
            'effects': {'stamina': 25},
            'description': 'Restores 25 Stamina instantly'
        },
        'greater_health_potion': {
            'name': 'Greater Health Potion',
            'emoji': '🍷',
            'type': 'consumable',
            'price': 75,
            'effects': {'heal': 100},
            'description': 'Restores 100 HP instantly'
        },
        'iron_sword': {
            'name': 'Iron Sword',
            'emoji': '⚔️',
            'type': 'weapon',
            'price': 150,
            'stats': {'attack': 10},
            'description': 'A sturdy iron blade. +10 Attack'
        },
        'steel_armor': {
            'name': 'Steel Armor',
            'emoji': '🛡️',
            'type': 'armor',
            'price': 200,
            'stats': {'defense': 12, 'max_hp': 20},
            'description': 'Heavy steel protection. +12 Defense, +20 HP'
        },
        'agility_boots': {
            'name': 'Agility Boots',
            'emoji': '👢',
            'type': 'armor',
            'price': 120,
            'stats': {'agility': 15},
            'description': 'Lightweight boots for speed. +15 Agility'
        },
        'elemental_focus': {
            'name': 'Elemental Focus',
            'emoji': '🔮',
            'type': 'accessory',
            'price': 300,
            'stats': {'element_power': 20, 'max_stamina': 15},
            'description': 'Amplifies elemental abilities. +20 Element Power, +15 Stamina'
        },
        'mithril_sword': {
            'name': 'Mithril Sword',
            'emoji': '⚔️',
            'type': 'weapon',
            'price': 500,
            'stats': {'attack': 25, 'agility': 5},
            'description': 'A legendary mithril blade. +25 Attack, +5 Agility'
        },
        'dragon_armor': {
            'name': 'Dragon Scale Armor',
            'emoji': '🛡️',
            'type': 'armor',
            'price': 750,
            'stats': {'defense': 30, 'max_hp': 50, 'element_power': 10},
            'description': 'Armor made from dragon scales. +30 Defense, +50 HP, +10 Element Power'
        },
        'master_focus': {
            'name': 'Master\'s Focus',
            'emoji': '💎',
            'type': 'accessory',
            'price': 1000,
            'stats': {'element_power': 40, 'max_stamina': 30, 'attack': 10},
            'description': 'A master craftsman\'s focus. +40 Element Power, +30 Stamina, +10 Attack'
        }
    }

    # Achievement definitions
    ACHIEVEMENTS = {
        'first_victory': {
            'name': 'First Victory',
            'description': 'Win your first battle',
            'emoji': '🎯',
            'reward': {'coins': 50, 'xp': 25}
        },
        'element_master': {
            'name': 'Element Master',
            'description': 'Deal 1000 element damage',
            'emoji': '🌟',
            'reward': {'coins': 200, 'xp': 100}
        },
        'level_10': {
            'name': 'Rising Warrior',
            'description': 'Reach level 10',
            'emoji': '📈',
            'reward': {'coins': 300, 'xp': 200}
        },
        'win_streak_5': {
            'name': 'Unstoppable',
            'description': 'Win 5 battles in a row',
            'emoji': '🔥',
            'reward': {'coins': 150, 'xp': 75}
        },
        'pvp_champion': {
            'name': 'PvP Champion',
            'description': 'Win 10 PvP battles',
            'emoji': '👑',
            'reward': {'coins': 500, 'xp': 300}
        },
        'explorer': {
            'name': 'Explorer',
            'description': 'Visit all locations',
            'emoji': '🗺️',
            'reward': {'coins': 400, 'xp': 250}
        },
        'rich_warrior': {
            'name': 'Wealthy Warrior',
            'description': 'Collect 5000 coins',
            'emoji': '💰',
            'reward': {'coins': 1000, 'xp': 500}
        },
        'daily_dedication': {
            'name': 'Daily Dedication',
            'description': 'Maintain a 7-day daily streak',
            'emoji': '📅',
            'reward': {'coins': 250, 'xp': 150}
        }
    }

    # Daily reward settings
    DAILY_REWARDS = {
        'base_coins': 50,
        'base_xp': 25,
        'max_streak_bonus': 2.0,  # 200% bonus at max streak
        'streak_bonus_per_day': 0.1  # 10% bonus per day
    }

    # Battle settings
    BATTLE_SETTINGS = {
        'max_turns': 50,
        'turn_timeout': 300,  # 5 minutes per turn
        'xp_loss_on_defeat': 0.1,  # 10% XP loss
        'coin_loss_on_defeat': 0.05,  # 5% coin loss
        'hp_loss_on_defeat': 0.5  # 50% HP loss
    }

    # PvP settings
    PVP_SETTINGS = {
        'challenge_timeout': 300,  # 5 minutes
        'battle_timeout': 1800,  # 30 minutes
        'winner_xp_bonus': 1.5,
        'winner_coin_bonus': 1.5,
        'level_difference_limit': 10  # Max level difference for PvP
    }

    # Rate limiting
    RATE_LIMITS = {
        'commands_per_minute': 10,
        'battles_per_hour': 20,
        'shop_purchases_per_hour': 30
    }

    # Starting player stats
    STARTING_STATS = {
        'level': 1,
        'experience': 0,
        'hp': 100,
        'max_hp': 100,
        'stamina': 50,
        'max_stamina': 50,
        'attack': 25,
        'defense': 20,
        'agility': 15,
        'element_power': 30,
        'coins': 100,
        'battles_won': 0,
        'battles_lost': 0,
        'daily_streak': 0
    }

    # Error messages
    ERROR_MESSAGES = {
        'player_not_found': "❌ Please use /start to create your character first!",
        'insufficient_funds': "❌ Not enough coins!",
        'insufficient_stamina': "❌ Not enough stamina!",
        'already_max_hp': "❌ You are already at full HP!",
        'battle_not_found': "❌ Battle not found or has ended.",
        'invalid_action': "❌ Invalid action!",
        'not_your_turn': "❌ It's not your turn!",
        'challenge_expired': "❌ Challenge code has expired.",
        'already_claimed_daily': "❌ You have already claimed your daily reward today!"
    }

    # Success messages
    SUCCESS_MESSAGES = {
        'player_created': "🎉 Welcome to Elemental RPG! Your character has been created!",
        'item_purchased': "✅ Item purchased successfully!",
        'daily_claimed': "🎁 Daily reward claimed!",
        'level_up': "🌟 LEVEL UP! All stats increased!",
        'battle_won': "🎉 Victory! You have defeated your enemy!",
        'challenge_created': "⚔️ PvP challenge created! Share the code with another player."
    }

    # Command descriptions for BotFather
    COMMAND_DESCRIPTIONS = {
        'start': 'Begin your RPG adventure',
        'menu': 'Show main menu',
        'profile': 'View your character stats',
        'travel': 'Explore different locations',
        'challenge': 'Create a PvP challenge',
        'join': 'Join a PvP battle',
        'shop': 'Visit the item shop',
        'daily': 'Claim daily rewards',
        'rankings': 'View player leaderboard',
        'help': 'Show help information'
    }

    # Webhook settings for production
    WEBHOOK_SETTINGS = {
        'url_path': BOT_TOKEN,
        'listen': '0.0.0.0',
        'port': int(os.getenv('PORT', 8080))
    }

    @classmethod
    def get_element_emoji(cls, element: str) -> str:
        """Get emoji for element"""
        return cls.ELEMENTS.get(element, {}).get('emoji', '❓')

    @classmethod
    def get_location_by_element(cls, element: str) -> str:
        """Get location name by element"""
        for location_name, location_data in cls.LOCATIONS.items():
            if location_data['element'] == element:
                return location_name
        return 'Unknown Location'

    @classmethod
    def validate_element(cls, element: str) -> bool:
        """Validate if element exists"""
        return element in cls.ELEMENTS

    @classmethod
    def get_shop_item(cls, item_id: str) -> dict:
        """Get shop item by ID"""
        return cls.SHOP_ITEMS.get(item_id, {})

    @classmethod
    def calculate_level_xp_requirement(cls, level: int) -> int:
        """Calculate XP required for a specific level"""
        return (level ** 2) * cls.BASE_XP_FORMULA

    @classmethod
    def get_daily_reward(cls, streak: int) -> dict:
        """Calculate daily reward based on streak"""
        base_coins = cls.DAILY_REWARDS['base_coins']
        base_xp = cls.DAILY_REWARDS['base_xp']

        # Calculate streak bonus
        streak_bonus = min(
            streak * cls.DAILY_REWARDS['streak_bonus_per_day'],
            cls.DAILY_REWARDS['max_streak_bonus']
        )

        coins = int(base_coins * (1 + streak_bonus))
        xp = int(base_xp * (1 + streak_bonus))

        return {
            'coins': coins,
            'xp': xp,
            'streak_bonus_percent': int(streak_bonus * 100)
        }
