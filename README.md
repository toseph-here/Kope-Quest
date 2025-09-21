# Kope-Quest
# Telegram RPG Bot

A complete text-based multiplayer RPG bot for Telegram with element system, combat mechanics, and admin features.

## Features

### 🎮 Core Game Features
- **8 Element System**: Fire, Ice, Lightning, Water, Earth, Shadow, Wind, Light
- **Element Effectiveness Matrix**: Rock-paper-scissors style combat with advantages/disadvantages
- **Turn-based Combat**: Attack, Defend, Heal, and Element Skills
- **NPC Battles**: Fight themed enemies across 8 different locations
- **PvP System**: Challenge other players with battle codes
- **Progression System**: Level up to increase all stats by +5
- **Economy System**: Earn and spend coins on weapons, armor, and potions

### 🛡️ Admin Features
- **Owner Panel**: Complete admin control (Owner ID: 8094286612)
- **Broadcast System**: Send messages to all users
- **Resource Donation**: Give coins/XP to specific users or everyone
- **Bot Statistics**: View user counts, battles, and more
- **God Mode**: Admin has full control over the game

### 📊 Player Features
- **Profile System**: Track stats, battles won/lost, daily streaks
- **Inventory Management**: Collect and use items
- **Daily Rewards**: Login bonuses with streak multipliers
- **Rankings**: Leaderboard system
- **Achievement System**: Unlock achievements for rewards

## Installation

### Prerequisites
- Python 3.9 or higher
- A Telegram Bot Token from [@BotFather](https://t.me/botfather)

### Local Development Setup

1. **Clone or download all the files:**
   - `main.py` - Main bot application
   - `database.py` - Database operations
   - `game_logic.py` - Core game mechanics
   - `config.py` - Game configuration
   - `requirements.txt` - Python dependencies
   - `vercel.json` - Deployment configuration
   - `.env.example` - Environment variables template

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your bot token:
   ```env
   BOT_TOKEN=your_bot_token_from_botfather
   OWNER_ID=your_telegram_user_id
   ENVIRONMENT=development
   ```

4. **Run the bot:**
   ```bash
   python main.py
   ```

## Vercel Deployment

### Step 1: Prepare for Deployment
1. Create a new repository on GitHub
2. Upload all the project files to your repository
3. Make sure your `vercel.json` is configured properly

### Step 2: Deploy to Vercel
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project" and import your GitHub repository
3. Set environment variables in Vercel:
   - `BOT_TOKEN` - Your Telegram bot token
   - `OWNER_ID` - Your Telegram user ID
   - `ENVIRONMENT` - Set to `production`
   - `WEBHOOK_URL` - Your Vercel app URL (e.g., `https://your-app.vercel.app`)

### Step 3: Set Webhook
After deployment, set your bot's webhook:
```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://your-app.vercel.app/<YOUR_BOT_TOKEN>"}'
```

## Bot Commands

### Player Commands
- `/start` - Begin your RPG adventure and choose your element
- `/menu` - Show the main menu with all options
- `/profile` - View your character stats and progress
- `/travel` - Explore locations and fight NPCs
- `/challenge` - Create a PvP challenge code
- `/join <code>` - Join another player's PvP battle
- `/shop` - Visit the item shop to buy equipment and potions
- `/daily` - Claim your daily reward (streak bonuses!)
- `/rankings` - View the top players leaderboard
- `/help` - Show detailed game help

### Admin Commands (Owner Only)
- `/owner` - Access the admin panel
- `/broadcast <message>` - Send message to all users
- `/donate coins <amount>` - Give coins to all players
- `/donate xp <amount>` - Give XP to all players  
- `/donate <user_id> coins <amount>` - Give coins to specific user
- `/donate <user_id> xp <amount>` - Give XP to specific user

## Game Mechanics

### Element System
The game uses an 8-element rock-paper-scissors system:

**Effectiveness Chain:**
- 🔥 Fire > ❄️ Ice > 🌊 Water > ⚡ Lightning > 🌍 Earth > 💨 Wind > 🌙 Shadow > 🌟 Light > 🔥 Fire

**Element Advantages:**
- **Effective (1.5x damage)**: Your element beats the enemy's element
- **Normal (1.0x damage)**: Neutral matchup
- **Weak (0.8x damage)**: Enemy's element beats yours

### Combat System

**Turn-based Actions:**
1. **Attack** - Basic damage based on Attack stat
2. **Defend** - Reduce incoming damage and restore stamina
3. **Heal** - Restore HP (costs 10 stamina)
4. **Element Skill** - Powerful elemental attack (costs 15 stamina)

**Damage Formula:**
```
Base Damage = (Attack - Defense×0.5) × Element_Effectiveness × Random(0.8-1.2)
Critical Hit = Base Damage × 1.5 (10% chance + agility bonus)
```

### Locations & Enemies

| Location | Element | Level Range | Description |
|----------|---------|-------------|-------------|
| 🌋 Burning Volcano | Fire | 1-5 | Volcanic region with fire creatures |
| 🏔️ Frozen Tundra | Ice | 3-8 | Freezing wasteland with ice enemies |
| ⛈️ Storm Peaks | Lightning | 5-12 | Lightning-struck mountain peaks |
| 🌊 Mystic Ocean | Water | 4-10 | Deep waters with aquatic creatures |
| 🏔️ Ancient Caverns | Earth | 6-15 | Underground caves with earth elementals |
| ☁️ Sky Gardens | Wind | 8-18 | Floating gardens in the clouds |
| 🌚 Dark Forest | Shadow | 10-22 | Mysterious shadow-shrouded forest |
| 🏛️ Sacred Temple | Light | 12-25 | Ancient temple of pure light energy |

### Shop Items

**Consumables:**
- 🧪 Health Potion (25 coins) - Restore 30 HP
- ⚗️ Stamina Potion (20 coins) - Restore 25 Stamina
- 🍷 Greater Health Potion (75 coins) - Restore 100 HP

**Equipment:**
- ⚔️ Iron Sword (150 coins) - +10 Attack
- 🛡️ Steel Armor (200 coins) - +12 Defense, +20 HP
- 👢 Agility Boots (120 coins) - +15 Agility
- 🔮 Elemental Focus (300 coins) - +20 Element Power, +15 Stamina

**Legendary Items:**
- ⚔️ Mithril Sword (500 coins) - +25 Attack, +5 Agility
- 🛡️ Dragon Scale Armor (750 coins) - +30 Defense, +50 HP, +10 Element Power
- 💎 Master's Focus (1000 coins) - +40 Element Power, +30 Stamina, +10 Attack

## Database Schema

The bot uses SQLite for development and can be configured for PostgreSQL in production.

### Tables:
- **players** - Player stats, progression, and metadata
- **inventory** - Player items and equipment
- **battle_history** - Record of all battles
- **achievements** - Unlocked player achievements

## File Structure

```
telegram-rpg-bot/
├── main.py              # Main bot application
├── database.py          # Database operations  
├── game_logic.py        # Core game mechanics
├── config.py            # Game configuration
├── requirements.txt     # Python dependencies
├── vercel.json         # Vercel deployment config
├── .env.example        # Environment variables template
└── README.md           # This file
```

## Configuration

All game balance and settings can be modified in `config.py`:

- **Element effectiveness multipliers**
- **Starting player stats**
- **XP and level requirements** 
- **Shop items and prices**
- **Location data and enemy types**
- **Daily reward amounts**
- **Battle settings and timeouts**

## Contributing

Feel free to fork this project and submit pull requests. Some areas for improvement:

- **Guild/Clan System** - Team up with other players
- **More Equipment Types** - Accessories, rings, etc.
- **Dungeon System** - Multi-floor adventures
- **Crafting System** - Create your own items
- **Tournament Mode** - Organized PvP competitions
- **Mobile-Responsive Web Interface** - Browser-based gameplay

## License

This project is open source. Feel free to use, modify, and distribute as needed.

## Support

If you encounter any issues:

1. Check that all environment variables are set correctly
2. Ensure your bot token is valid and the bot is active
3. Verify that all dependencies are installed
4. Check the logs for specific error messages

For the admin panel, make sure your Telegram user ID is correctly set as `OWNER_ID` in the environment variables.

## Credits

Developed as a comprehensive example of a Telegram bot with:
- Advanced game mechanics
- Database integration
- Admin functionality  
- Production deployment ready
- Clean, modular code structure

Enjoy your RPG adventure! ⚔️🎮
