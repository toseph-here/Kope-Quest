"""
Telegram RPG Bot - Main Bot File
Complete text-based multiplayer RPG bot with element system, combat, and admin features.
"""

import asyncio
import logging
import os
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

from database import Database
from game_logic import GameLogic, Player, NPC
from config import Config

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
ELEMENT_SELECTION = 1
BATTLE_ACTION = 2
CHALLENGE_CODE = 3

class TelegramRPGBot:
    def __init__(self):
        self.db = Database()
        self.game_logic = GameLogic()
        self.active_battles: Dict[str, Dict] = {}
        self.active_challenges: Dict[str, Dict] = {}

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user

        try:
            # Check if player exists
            player_data = await self.db.get_player(user.id)

            if player_data:
                await update.message.reply_text(
                    f"Welcome back, {player_data['username']}! 🎮\n"
                    f"Your Element: {Config.ELEMENTS[player_data['element']]['emoji']} {player_data['element']}\n\n"
                    "Use /menu to continue your adventure!"
                )
                return

            # New player - show element selection
            await self.show_element_selection(update, context)

        except Exception as e:
            logger.error(f"Error in start command: {e}")
            await update.message.reply_text("⚠️ An error occurred. Please try again.")

    async def show_element_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show element selection for new players"""
        keyboard = []
        elements = list(Config.ELEMENTS.keys())

        # Create 2x4 grid of elements
        for i in range(0, len(elements), 2):
            row = []
            for j in range(2):
                if i + j < len(elements):
                    element = elements[i + j]
                    emoji = Config.ELEMENTS[element]['emoji']
                    row.append(InlineKeyboardButton(f"{emoji} {element}", callback_data=f"element_{element}"))
            keyboard.append(row)

        reply_markup = InlineKeyboardMarkup(keyboard)

        welcome_text = (
            "🎮 **Welcome to Elemental RPG!** 🎮\n\n"
            "Choose your elemental affinity to begin your journey:\n\n"
            "🔥 **Fire** - Fierce and destructive\n"
            "❄️ **Ice** - Cold and controlling\n"
            "⚡ **Lightning** - Fast and shocking\n"
            "🌊 **Water** - Flowing and adaptable\n"
            "🌍 **Earth** - Strong and enduring\n"
            "🌙 **Shadow** - Mysterious and cunning\n"
            "💨 **Wind** - Swift and free\n"
            "🌟 **Light** - Pure and healing\n\n"
            "Choose wisely - your element affects combat effectiveness!"
        )

        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

    async def handle_element_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle element selection callback"""
        query = update.callback_query
        await query.answer()

        user = query.from_user
        element = query.data.replace("element_", "")

        try:
            # Create new player
            success = await self.db.create_player(
                user_id=user.id,
                username=user.username or user.first_name,
                element=element
            )

            if success:
                element_info = Config.ELEMENTS[element]
                await query.edit_message_text(
                    f"🎉 **Welcome, {element_info['emoji']} {element} Warrior!** 🎉\n\n"
                    f"You have chosen the path of {element}!\n"
                    f"Starting stats:\n"
                    f"❤️ HP: 100\n"
                    f"⚡ Stamina: 50\n"
                    f"⚔️ Attack: 25\n"
                    f"🛡️ Defense: 20\n"
                    f"💨 Agility: 15\n"
                    f"🌟 Element Power: 30\n"
                    f"💰 Coins: 100\n\n"
                    "Use /menu to start your adventure!",
                    parse_mode='Markdown'
                )
            else:
                await query.edit_message_text("❌ Failed to create character. Please try again.")

        except Exception as e:
            logger.error(f"Error in element selection: {e}")
            await query.edit_message_text("⚠️ An error occurred. Please try again.")

    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show main menu"""
        user_id = update.effective_user.id

        try:
            player_data = await self.db.get_player(user_id)
            if not player_data:
                await update.message.reply_text("❌ Please use /start to create your character first!")
                return

            keyboard = [
                [KeyboardButton("📊 Profile"), KeyboardButton("🗺️ Travel")],
                [KeyboardButton("⚔️ Challenge Player"), KeyboardButton("🏪 Shop")],
                [KeyboardButton("🎒 Inventory"), KeyboardButton("🏆 Rankings")],
                [KeyboardButton("🎁 Daily Reward"), KeyboardButton("❓ Help")]
            ]

            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

            element_emoji = Config.ELEMENTS[player_data['element']]['emoji']

            await update.message.reply_text(
                f"🎮 **Main Menu** 🎮\n\n"
                f"Welcome, {element_emoji} {player_data['username']}!\n"
                f"Level {player_data['level']} {player_data['element']} Warrior\n\n"
                "What would you like to do?",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

        except Exception as e:
            logger.error(f"Error in menu command: {e}")
            await update.message.reply_text("⚠️ An error occurred. Please try again.")

    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show player profile"""
        user_id = update.effective_user.id

        try:
            player_data = await self.db.get_player(user_id)
            if not player_data:
                await update.message.reply_text("❌ Please use /start to create your character first!")
                return

            element_info = Config.ELEMENTS[player_data['element']]
            xp_needed = (player_data['level'] ** 2) * 100 - player_data['experience']

            profile_text = (
                f"📊 **{player_data['username']}'s Profile** 📊\n\n"
                f"🌟 Element: {element_info['emoji']} {player_data['element']}\n"
                f"📈 Level: {player_data['level']}\n"
                f"⭐ XP: {player_data['experience']} (Need {xp_needed} for next level)\n\n"
                f"❤️ HP: {player_data['hp']}/{player_data['max_hp']}\n"
                f"⚡ Stamina: {player_data['stamina']}/{player_data['max_stamina']}\n"
                f"⚔️ Attack: {player_data['attack']}\n"
                f"🛡️ Defense: {player_data['defense']}\n"
                f"💨 Agility: {player_data['agility']}\n"
                f"🌟 Element Power: {player_data['element_power']}\n\n"
                f"💰 Coins: {player_data['coins']}\n"
                f"🏆 Battles Won: {player_data['battles_won']}\n"
                f"💀 Battles Lost: {player_data['battles_lost']}\n"
                f"🔥 Daily Streak: {player_data['daily_streak']}"
            )

            await update.message.reply_text(profile_text, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Error in profile command: {e}")
            await update.message.reply_text("⚠️ An error occurred. Please try again.")

# Continue with the rest of the bot implementation...


    async def travel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show travel locations"""
        user_id = update.effective_user.id

        try:
            player_data = await self.db.get_player(user_id)
            if not player_data:
                await update.message.reply_text("❌ Please use /start to create your character first!")
                return

            if player_data['hp'] <= 0:
                await update.message.reply_text("💀 You need to heal before traveling! Visit the shop for healing potions.")
                return

            keyboard = []
            for location_name, location_data in Config.LOCATIONS.items():
                keyboard.append([InlineKeyboardButton(
                    f"{location_data['emoji']} {location_name} (Lv.{location_data['min_level']}-{location_data['max_level']})",
                    callback_data=f"travel_{location_name}"
                )])

            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                "🗺️ **Choose your destination:** 🗺️\n\n"
                "Each location has different enemies and rewards!\n"
                "Higher level areas give better rewards but are more dangerous.",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

        except Exception as e:
            logger.error(f"Error in travel command: {e}")
            await update.message.reply_text("⚠️ An error occurred. Please try again.")

    async def handle_travel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle travel location selection"""
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        location = query.data.replace("travel_", "")

        try:
            player_data = await self.db.get_player(user_id)
            location_data = Config.LOCATIONS[location]

            # Generate random enemy
            enemy_type = random.choice(location_data['enemy_types'])
            enemy_level = random.randint(location_data['min_level'], location_data['max_level'])

            npc = self.game_logic.create_npc(enemy_type, enemy_level, location_data['element'])

            # Store battle data
            battle_id = f"npc_{user_id}_{int(datetime.now().timestamp())}"
            self.active_battles[battle_id] = {
                'type': 'npc',
                'player_id': user_id,
                'npc': npc,
                'location': location,
                'turn': 'player'
            }

            keyboard = [
                [InlineKeyboardButton("⚔️ FIGHT!", callback_data=f"fight_{battle_id}")],
                [InlineKeyboardButton("🏃 Run Away", callback_data=f"run_{battle_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                f"🌍 **{location}** 🌍\n\n"
                f"You encounter a wild {npc.name}!\n"
                f"Level: {npc.level}\n"
                f"Element: {Config.ELEMENTS[npc.element]['emoji']} {npc.element}\n"
                f"HP: {npc.hp}/{npc.max_hp}\n\n"
                "What do you want to do?",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

        except Exception as e:
            logger.error(f"Error in travel handler: {e}")
            await query.edit_message_text("⚠️ An error occurred. Please try again.")

    async def challenge_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Create PvP challenge"""
        user_id = update.effective_user.id

        try:
            player_data = await self.db.get_player(user_id)
            if not player_data:
                await update.message.reply_text("❌ Please use /start to create your character first!")
                return

            if player_data['hp'] <= 0:
                await update.message.reply_text("💀 You need to heal before challenging other players!")
                return

            # Generate unique challenge code
            challenge_code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))

            # Store challenge
            self.active_challenges[challenge_code] = {
                'challenger_id': user_id,
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(minutes=5)
            }

            await update.message.reply_text(
                f"⚔️ **PvP Challenge Created!** ⚔️\n\n"
                f"Challenge Code: `{challenge_code}`\n\n"
                f"Share this code with another player so they can use:\n"
                f"`/join {challenge_code}`\n\n"
                f"⏰ Code expires in 5 minutes.",
                parse_mode='Markdown'
            )

        except Exception as e:
            logger.error(f"Error in challenge command: {e}")
            await update.message.reply_text("⚠️ An error occurred. Please try again.")

    async def join_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Join PvP challenge"""
        user_id = update.effective_user.id

        if not context.args:
            await update.message.reply_text("❌ Please provide a challenge code: `/join CODE123`", parse_mode='Markdown')
            return

        challenge_code = context.args[0].upper()

        try:
            player_data = await self.db.get_player(user_id)
            if not player_data:
                await update.message.reply_text("❌ Please use /start to create your character first!")
                return

            if player_data['hp'] <= 0:
                await update.message.reply_text("💀 You need to heal before joining battles!")
                return

            if challenge_code not in self.active_challenges:
                await update.message.reply_text("❌ Invalid or expired challenge code.")
                return

            challenge = self.active_challenges[challenge_code]

            # Check if expired
            if datetime.now() > challenge['expires_at']:
                del self.active_challenges[challenge_code]
                await update.message.reply_text("❌ Challenge code has expired.")
                return

            challenger_id = challenge['challenger_id']

            if user_id == challenger_id:
                await update.message.reply_text("❌ You cannot challenge yourself!")
                return

            # Get challenger data
            challenger_data = await self.db.get_player(challenger_id)
            if not challenger_data or challenger_data['hp'] <= 0:
                await update.message.reply_text("❌ Challenger is not available for battle.")
                return

            # Start PvP battle
            battle_id = f"pvp_{challenger_id}_{user_id}_{int(datetime.now().timestamp())}"
            self.active_battles[battle_id] = {
                'type': 'pvp',
                'player1_id': challenger_id,
                'player2_id': user_id,
                'current_turn': challenger_id,
                'turn_count': 1,
                'battle_log': []
            }

            # Remove challenge
            del self.active_challenges[challenge_code]

            # Notify both players
            await update.message.reply_text(
                f"⚔️ **PvP Battle Started!** ⚔️\n\n"
                f"You vs {challenger_data['username']}\n"
                f"Battle will be conducted in private messages!\n\n"
                f"Check your DMs for battle actions!"
            )

            try:
                await context.bot.send_message(
                    chat_id=challenger_id,
                    text=f"⚔️ **PvP Battle Started!** ⚔️\n\n"
                         f"You vs {player_data['username']}\n"
                         f"It's your turn! Choose your action below:"
                )
                await self.send_pvp_battle_menu(context.bot, challenger_id, battle_id)

                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"⚔️ **Battle in Progress** ⚔️\n\n"
                         f"Waiting for {challenger_data['username']} to make their move..."
                )
            except Exception as e:
                logger.error(f"Error sending PvP battle messages: {e}")

        except Exception as e:
            logger.error(f"Error in join command: {e}")
            await update.message.reply_text("⚠️ An error occurred. Please try again.")

    async def send_pvp_battle_menu(self, bot, user_id: int, battle_id: str):
        """Send PvP battle action menu to player"""
        keyboard = [
            [InlineKeyboardButton("⚔️ Attack", callback_data=f"pvp_attack_{battle_id}")],
            [InlineKeyboardButton("🛡️ Defend", callback_data=f"pvp_defend_{battle_id}")],
            [InlineKeyboardButton("💚 Heal", callback_data=f"pvp_heal_{battle_id}")],
            [InlineKeyboardButton("🌟 Element Skill", callback_data=f"pvp_element_{battle_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            await bot.send_message(
                chat_id=user_id,
                text="Choose your battle action:",
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Error sending PvP menu: {e}")

    async def shop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show shop menu"""
        user_id = update.effective_user.id

        try:
            player_data = await self.db.get_player(user_id)
            if not player_data:
                await update.message.reply_text("❌ Please use /start to create your character first!")
                return

            keyboard = []
            for item_id, item_data in Config.SHOP_ITEMS.items():
                keyboard.append([InlineKeyboardButton(
                    f"{item_data['emoji']} {item_data['name']} - {item_data['price']}💰",
                    callback_data=f"buy_{item_id}"
                )])

            reply_markup = InlineKeyboardMarkup(keyboard)

            shop_text = (
                f"🏪 **Elemental Shop** 🏪\n\n"
                f"💰 Your Coins: {player_data['coins']}\n\n"
                f"**Available Items:**\n"
            )

            for item_data in Config.SHOP_ITEMS.values():
                effect_text = ""
                if item_data['type'] == 'consumable':
                    if 'heal' in item_data['effects']:
                        effect_text = f"Heals {item_data['effects']['heal']} HP"
                    elif 'stamina' in item_data['effects']:
                        effect_text = f"Restores {item_data['effects']['stamina']} Stamina"
                elif item_data['type'] in ['weapon', 'armor']:
                    effects = [f"+{v} {k}" for k, v in item_data['stats'].items()]
                    effect_text = ", ".join(effects)

                shop_text += f"{item_data['emoji']} **{item_data['name']}** - {item_data['price']}💰\n{effect_text}\n\n"

            await update.message.reply_text(shop_text, reply_markup=reply_markup, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Error in shop command: {e}")
            await update.message.reply_text("⚠️ An error occurred. Please try again.")

    async def handle_purchase(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle item purchase"""
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        item_id = query.data.replace("buy_", "")

        try:
            player_data = await self.db.get_player(user_id)
            item_data = Config.SHOP_ITEMS[item_id]

            if player_data['coins'] < item_data['price']:
                await query.edit_message_text("❌ Not enough coins!")
                return

            # Handle different item types
            if item_data['type'] == 'consumable':
                if 'heal' in item_data['effects']:
                    heal_amount = min(item_data['effects']['heal'], player_data['max_hp'] - player_data['hp'])
                    if heal_amount <= 0:
                        await query.edit_message_text("❌ You are already at full HP!")
                        return

                    await self.db.update_player_stats(user_id, {
                        'hp': player_data['hp'] + heal_amount,
                        'coins': player_data['coins'] - item_data['price']
                    })

                    await query.edit_message_text(
                        f"✅ Used {item_data['name']}!\n"
                        f"❤️ Healed {heal_amount} HP\n"
                        f"💰 -{item_data['price']} coins"
                    )

                elif 'stamina' in item_data['effects']:
                    stamina_amount = min(item_data['effects']['stamina'], player_data['max_stamina'] - player_data['stamina'])
                    if stamina_amount <= 0:
                        await query.edit_message_text("❌ You are already at full stamina!")
                        return

                    await self.db.update_player_stats(user_id, {
                        'stamina': player_data['stamina'] + stamina_amount,
                        'coins': player_data['coins'] - item_data['price']
                    })

                    await query.edit_message_text(
                        f"✅ Used {item_data['name']}!\n"
                        f"⚡ Restored {stamina_amount} Stamina\n"
                        f"💰 -{item_data['price']} coins"
                    )

            elif item_data['type'] in ['weapon', 'armor']:
                # Add to inventory (simplified - just apply stats for now)
                stat_updates = {'coins': player_data['coins'] - item_data['price']}
                stat_updates.update(item_data['stats'])

                await self.db.increase_player_stats(user_id, stat_updates)

                stats_text = ", ".join([f"+{v} {k}" for k, v in item_data['stats'].items()])
                await query.edit_message_text(
                    f"✅ Purchased {item_data['name']}!\n"
                    f"📈 {stats_text}\n"
                    f"💰 -{item_data['price']} coins"
                )

        except Exception as e:
            logger.error(f"Error in purchase: {e}")
            await query.edit_message_text("⚠️ An error occurred. Please try again.")

    async def daily_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle daily reward claim"""
        user_id = update.effective_user.id

        try:
            player_data = await self.db.get_player(user_id)
            if not player_data:
                await update.message.reply_text("❌ Please use /start to create your character first!")
                return

            # Check if already claimed today
            today = datetime.now().strftime('%Y-%m-%d')
            if player_data['last_daily_claim'] == today:
                await update.message.reply_text("❌ You have already claimed your daily reward today!")
                return

            # Calculate streak
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            if player_data['last_daily_claim'] == yesterday:
                new_streak = player_data['daily_streak'] + 1
            else:
                new_streak = 1

            # Calculate rewards based on streak
            base_coins = 50
            base_xp = 25

            streak_bonus = min(new_streak * 0.1, 2.0)  # Max 200% bonus at 20-day streak
            coin_reward = int(base_coins * (1 + streak_bonus))
            xp_reward = int(base_xp * (1 + streak_bonus))

            # Update player
            await self.db.update_player_stats(user_id, {
                'coins': player_data['coins'] + coin_reward,
                'experience': player_data['experience'] + xp_reward,
                'last_daily_claim': today,
                'daily_streak': new_streak
            })

            # Check for level up
            new_xp = player_data['experience'] + xp_reward
            level_up_text = ""
            xp_for_next_level = (player_data['level'] ** 2) * 100

            if new_xp >= xp_for_next_level:
                new_level = player_data['level'] + 1
                level_up_text = await self.handle_level_up(user_id, new_level)

            reward_text = (
                f"🎁 **Daily Reward Claimed!** 🎁\n\n"
                f"💰 +{coin_reward} coins\n"
                f"⭐ +{xp_reward} XP\n"
                f"🔥 Streak: {new_streak} days\n"
                f"📈 Streak Bonus: {int(streak_bonus * 100)}%\n\n"
                f"{level_up_text}"
                f"Come back tomorrow for more rewards!"
            )

            await update.message.reply_text(reward_text, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Error in daily command: {e}")
            await update.message.reply_text("⚠️ An error occurred. Please try again.")

    async def rankings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show player rankings"""
        try:
            # Get top players by level and XP
            top_players = await self.db.get_top_players(limit=10)

            if not top_players:
                await update.message.reply_text("❌ No players found in rankings.")
                return

            rankings_text = "🏆 **Top Players Leaderboard** 🏆\n\n"

            medals = ["🥇", "🥈", "🥉"] + ["🏅"] * 7

            for i, player in enumerate(top_players):
                element_emoji = Config.ELEMENTS[player['element']]['emoji']
                rankings_text += (
                    f"{medals[i]} **#{i+1}** {element_emoji} {player['username']}\n"
                    f"   Level {player['level']} • {player['experience']} XP\n"
                    f"   🏆 {player['battles_won']}W - {player['battles_lost']}L\n\n"
                )

            await update.message.reply_text(rankings_text, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Error in rankings command: {e}")
            await update.message.reply_text("⚠️ An error occurred. Please try again.")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help information"""
        help_text = (
            "❓ **Elemental RPG Help** ❓\n\n"
            "**Commands:**\n"
            "• `/start` - Begin your adventure\n"
            "• `/menu` - Main menu\n"
            "• `/profile` - View your stats\n"
            "• `/travel` - Explore locations\n"
            "• `/challenge` - Create PvP challenge\n"
            "• `/join <code>` - Join PvP battle\n"
            "• `/shop` - Buy items\n"
            "• `/daily` - Claim daily reward\n"
            "• `/rankings` - View leaderboard\n\n"
            "**Element System:**\n"
            "🔥 Fire > ❄️ Ice > 🌊 Water > ⚡ Lightning > 🌍 Earth > 💨 Wind > 🌙 Shadow > 🌟 Light > 🔥 Fire\n\n"
            "**Combat Actions:**\n"
            "• **Attack** - Deal damage to enemy\n"
            "• **Defend** - Reduce incoming damage\n"
            "• **Heal** - Restore HP (costs stamina)\n"
            "• **Element Skill** - Powerful elemental attack (costs stamina)\n\n"
            "**Tips:**\n"
            "• Fight enemies to gain XP and coins\n"
            "• Level up increases all stats by +5\n"
            "• Use daily rewards to maintain your streak\n"
            "• Element effectiveness gives 1.5x damage advantage\n"
            "• Critical hits have 10% chance for 1.5x damage"
        )

        await update.message.reply_text(help_text, parse_mode='Markdown')

    # Owner commands
    async def owner_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Owner panel command"""
        if update.effective_user.id != Config.OWNER_ID:
            await update.message.reply_text("❌ You don't have permission to use this command.")
            return

        keyboard = [
            [InlineKeyboardButton("📢 Broadcast Message", callback_data="owner_broadcast")],
            [InlineKeyboardButton("💰 Donate Coins (All)", callback_data="owner_donate_coins")],
            [InlineKeyboardButton("⭐ Donate XP (All)", callback_data="owner_donate_xp")],
            [InlineKeyboardButton("📊 Bot Stats", callback_data="owner_stats")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "🛡️ **Owner Panel** 🛡️\n\n"
            "Choose an administrative action:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def broadcast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Broadcast message to all users"""
        if update.effective_user.id != Config.OWNER_ID:
            return

        if not context.args:
            await update.message.reply_text("Usage: /broadcast <message>")
            return

        message = ' '.join(context.args)
        users = await self.db.get_all_users()
        success_count = 0

        for user in users:
            try:
                await context.bot.send_message(
                    chat_id=user['user_id'],
                    text=f"📢 **Admin Broadcast** 📢\n\n{message}",
                    parse_mode='Markdown'
                )
                success_count += 1
                await asyncio.sleep(0.1)  # Rate limiting
            except Exception as e:
                logger.error(f"Failed to send broadcast to {user['user_id']}: {e}")

        await update.message.reply_text(f"✅ Broadcast sent to {success_count}/{len(users)} users.")

    async def donate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Donate resources to players"""
        if update.effective_user.id != Config.OWNER_ID:
            return

        if len(context.args) < 2:
            await update.message.reply_text(
                "Usage:\n"
                "/donate coins <amount> - Give coins to all players\n"
                "/donate xp <amount> - Give XP to all players\n"
                "/donate <user_id> coins <amount> - Give coins to specific user\n"
                "/donate <user_id> xp <amount> - Give XP to specific user"
            )
            return

        try:
            if context.args[0].isdigit():
                # Donate to specific user
                user_id = int(context.args[0])
                resource_type = context.args[1].lower()
                amount = int(context.args[2])

                player = await self.db.get_player(user_id)
                if not player:
                    await update.message.reply_text("❌ User not found.")
                    return

                if resource_type == 'coins':
                    await self.db.update_player_stats(user_id, {'coins': player['coins'] + amount})
                elif resource_type == 'xp':
                    await self.db.update_player_stats(user_id, {'experience': player['experience'] + amount})
                else:
                    await update.message.reply_text("❌ Invalid resource type. Use 'coins' or 'xp'.")
                    return

                await update.message.reply_text(f"✅ Donated {amount} {resource_type} to user {user_id}.")

                # Notify the user
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"🎁 **Admin Gift!** 🎁\n\nYou received {amount} {resource_type}!",
                        parse_mode='Markdown'
                    )
                except:
                    pass

            else:
                # Donate to all users
                resource_type = context.args[0].lower()
                amount = int(context.args[1])

                if resource_type not in ['coins', 'xp']:
                    await update.message.reply_text("❌ Invalid resource type. Use 'coins' or 'xp'.")
                    return

                users = await self.db.get_all_users()
                success_count = 0

                for user in users:
                    try:
                        if resource_type == 'coins':
                            await self.db.update_player_stats(user['user_id'], {'coins': user['coins'] + amount})
                        elif resource_type == 'xp':
                            await self.db.update_player_stats(user['user_id'], {'experience': user['experience'] + amount})

                        # Notify user
                        try:
                            await context.bot.send_message(
                                chat_id=user['user_id'],
                                text=f"🎁 **Admin Gift!** 🎁\n\nEveryone received {amount} {resource_type}!",
                                parse_mode='Markdown'
                            )
                        except:
                            pass

                        success_count += 1
                        await asyncio.sleep(0.1)  # Rate limiting
                    except Exception as e:
                        logger.error(f"Failed to donate to {user['user_id']}: {e}")

                await update.message.reply_text(f"✅ Donated {amount} {resource_type} to {success_count}/{len(users)} users.")

        except ValueError:
            await update.message.reply_text("❌ Invalid amount. Please enter a number.")
        except Exception as e:
            logger.error(f"Error in donate command: {e}")
            await update.message.reply_text("❌ An error occurred.")

    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all callback queries"""
        query = update.callback_query
        data = query.data

        try:
            if data.startswith("element_"):
                await self.handle_element_selection(update, context)
            elif data.startswith("travel_"):
                await self.handle_travel(update, context)
            elif data.startswith("fight_"):
                await self.handle_npc_battle_start(update, context)
            elif data.startswith("run_"):
                await self.handle_run_away(update, context)
            elif data.startswith("action_"):
                await self.handle_battle_action(update, context)
            elif data.startswith("buy_"):
                await self.handle_purchase(update, context)
            elif data.startswith("pvp_"):
                await self.handle_pvp_action(update, context)
            elif data.startswith("owner_"):
                await self.handle_owner_callback(update, context)

        except Exception as e:
            logger.error(f"Error in callback query handler: {e}")
            await query.answer("⚠️ An error occurred.", show_alert=True)

    async def handle_pvp_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle PvP battle actions"""
        query = update.callback_query
        await query.answer()

        parts = query.data.split('_')
        action = parts[1]
        battle_id = '_'.join(parts[2:])

        user_id = query.from_user.id

        if battle_id not in self.active_battles:
            await query.edit_message_text("❌ Battle not found or has ended.")
            return

        battle = self.active_battles[battle_id]

        if battle['current_turn'] != user_id:
            await query.answer("❌ It's not your turn!", show_alert=True)
            return

        try:
            # Get both players
            player1_data = await self.db.get_player(battle['player1_id'])
            player2_data = await self.db.get_player(battle['player2_id'])

            current_player = Player(player1_data if user_id == battle['player1_id'] else player2_data)
            opponent = Player(player2_data if user_id == battle['player1_id'] else player1_data)

            # Execute action
            result = await self.game_logic.execute_battle_action(current_player, opponent, action)
            battle['battle_log'].append(result['log'])

            # Update database
            await self.db.update_player_stats(current_player.user_id, {
                'hp': current_player.hp,
                'stamina': current_player.stamina
            })

            # Check if battle ended
            if result['winner']:
                await self.handle_pvp_battle_end(context.bot, battle_id, result)
                return

            # Switch turns
            battle['current_turn'] = battle['player2_id'] if battle['current_turn'] == battle['player1_id'] else battle['player1_id']
            battle['turn_count'] += 1

            # Send messages to both players
            await self.update_pvp_battle_status(context.bot, battle_id)

        except Exception as e:
            logger.error(f"Error in PvP action: {e}")
            await query.edit_message_text("⚠️ An error occurred during battle.")

    async def handle_pvp_battle_end(self, bot, battle_id: str, result: Dict):
        """Handle PvP battle end"""
        battle = self.active_battles[battle_id]

        winner_id = battle['player1_id'] if result['winner'] == 'player' else battle['player2_id']
        loser_id = battle['player2_id'] if winner_id == battle['player1_id'] else battle['player1_id']

        # Update stats
        winner_data = await self.db.get_player(winner_id)
        loser_data = await self.db.get_player(loser_id)

        # Winner rewards
        xp_reward = loser_data['level'] * 30
        coin_reward = loser_data['level'] * 15

        await self.db.update_player_stats(winner_id, {
            'battles_won': winner_data['battles_won'] + 1,
            'experience': winner_data['experience'] + xp_reward,
            'coins': winner_data['coins'] + coin_reward
        })

        await self.db.update_player_stats(loser_id, {
            'battles_lost': loser_data['battles_lost'] + 1,
            'hp': max(1, loser_data['hp'] // 2)  # Lose half HP
        })

        # Notify both players
        battle_log = "\n".join(battle['battle_log'][-5:])  # Last 5 actions

        try:
            await bot.send_message(
                chat_id=winner_id,
                text=f"🎉 **PvP VICTORY!** 🎉\n\n"
                     f"You defeated {loser_data['username']}!\n\n"
                     f"**Rewards:**\n"
                     f"⭐ +{xp_reward} XP\n"
                     f"💰 +{coin_reward} coins\n\n"
                     f"**Battle Summary:**\n{battle_log}",
                parse_mode='Markdown'
            )

            await bot.send_message(
                chat_id=loser_id,
                text=f"💀 **PvP DEFEAT** 💀\n\n"
                     f"You were defeated by {winner_data['username']}...\n\n"
                     f"Don't give up! Train more and challenge them again!\n\n"
                     f"**Battle Summary:**\n{battle_log}",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error sending PvP end messages: {e}")

        # Clean up battle
        del self.active_battles[battle_id]

    async def update_pvp_battle_status(self, bot, battle_id: str):
        """Update PvP battle status for both players"""
        battle = self.active_battles[battle_id]

        player1_data = await self.db.get_player(battle['player1_id'])
        player2_data = await self.db.get_player(battle['player2_id'])

        current_turn_name = player1_data['username'] if battle['current_turn'] == battle['player1_id'] else player2_data['username']

        battle_status = (
            f"⚔️ **PvP Battle - Turn {battle['turn_count']}** ⚔️\n\n"
            f"👤 **{player1_data['username']}:** {player1_data['hp']}/{player1_data['max_hp']} HP\n"
            f"👤 **{player2_data['username']}:** {player2_data['hp']}/{player2_data['max_hp']} HP\n\n"
            f"🔄 **{current_turn_name}'s Turn**"
        )

        if battle['battle_log']:
            latest_action = battle['battle_log'][-1]
            battle_status += f"\n\n**Last Action:**\n{latest_action}"

        # Send to current turn player
        try:
            await self.send_pvp_battle_menu(bot, battle['current_turn'], battle_id)

            # Send status to waiting player
            waiting_player = battle['player2_id'] if battle['current_turn'] == battle['player1_id'] else battle['player1_id']
            await bot.send_message(
                chat_id=waiting_player,
                text=f"{battle_status}\n\nWaiting for their move...",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error updating PvP status: {e}")

    async def handle_owner_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle owner panel callbacks"""
        query = update.callback_query
        await query.answer()

        if update.effective_user.id != Config.OWNER_ID:
            return

        if query.data == "owner_stats":
            users = await self.db.get_all_users()
            total_users = len(users)
            active_battles = len(self.active_battles)
            active_challenges = len(self.active_challenges)

            # Get level distribution
            level_dist = {}
            for user in users:
                level = user['level']
                level_dist[level] = level_dist.get(level, 0) + 1

            stats_text = (
                f"📊 **Bot Statistics** 📊\n\n"
                f"👥 Total Users: {total_users}\n"
                f"⚔️ Active Battles: {active_battles}\n"
                f"🎯 Active Challenges: {active_challenges}\n\n"
                f"**Level Distribution:**\n"
            )

            for level in sorted(level_dist.keys()):
                stats_text += f"Level {level}: {level_dist[level]} players\n"

            await query.edit_message_text(stats_text, parse_mode='Markdown')

    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages (menu buttons)"""
        text = update.message.text
        user_id = update.effective_user.id

        # Check if player exists
        player_data = await self.db.get_player(user_id)
        if not player_data and text != "/start":
            await update.message.reply_text("❌ Please use /start to create your character first!")
            return

        if text == "📊 Profile":
            await self.profile_command(update, context)
        elif text == "🗺️ Travel":
            await self.travel_command(update, context)
        elif text == "⚔️ Challenge Player":
            await self.challenge_command(update, context)
        elif text == "🏪 Shop":
            await self.shop_command(update, context)
        elif text == "🎒 Inventory":
            await update.message.reply_text("🎒 Inventory system coming soon!")
        elif text == "🏆 Rankings":
            await self.rankings_command(update, context)
        elif text == "🎁 Daily Reward":
            await self.daily_command(update, context)
        elif text == "❓ Help":
            await self.help_command(update, context)

    async def handle_level_up(self, user_id: int, new_level: int) -> str:
        """Handle player level up"""
        stat_increases = {
            'level': new_level,
            'max_hp': 100 + (new_level - 1) * 5,  # Set absolute values
            'max_stamina': 50 + (new_level - 1) * 5,
            'attack': 25 + (new_level - 1) * 5,
            'defense': 20 + (new_level - 1) * 5,
            'agility': 15 + (new_level - 1) * 5,
            'element_power': 30 + (new_level - 1) * 5,
            'hp': 100 + (new_level - 1) * 5,  # Full heal on level up
            'stamina': 50 + (new_level - 1) * 5
        }

        await self.db.update_player_stats(user_id, stat_increases)

        return (
            f"🌟 **LEVEL UP!** 🌟\n"
            f"You reached Level {new_level}!\n\n"
            f"**All stats increased by +5!**\n"
            f"You have been fully healed!\n\n"
        )


def main():
    """Main function to run the bot"""
    # Initialize bot
    bot = TelegramRPGBot()

    # Build application
    application = Application.builder().token(os.getenv('BOT_TOKEN')).build()

    # Add handlers
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CommandHandler("menu", bot.menu_command))
    application.add_handler(CommandHandler("profile", bot.profile_command))
    application.add_handler(CommandHandler("travel", bot.travel_command))
    application.add_handler(CommandHandler("challenge", bot.challenge_command))
    application.add_handler(CommandHandler("join", bot.join_command))
    application.add_handler(CommandHandler("shop", bot.shop_command))
    application.add_handler(CommandHandler("daily", bot.daily_command))
    application.add_handler(CommandHandler("rankings", bot.rankings_command))
    application.add_handler(CommandHandler("help", bot.help_command))

    # Owner commands
    application.add_handler(CommandHandler("owner", bot.owner_command))
    application.add_handler(CommandHandler("broadcast", bot.broadcast_command))
    application.add_handler(CommandHandler("donate", bot.donate_command))

    # Callback query handler
    application.add_handler(CallbackQueryHandler(bot.handle_callback_query))

    # Message handler for menu buttons
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_text_message))

    # Start bot
    if os.getenv('ENVIRONMENT') == 'production':
        # Webhook for production
        application.run_webhook(
            listen="0.0.0.0",
            port=int(os.getenv("PORT", 8080)),
            url_path=os.getenv('BOT_TOKEN'),
            webhook_url=f"{os.getenv('WEBHOOK_URL')}/{os.getenv('BOT_TOKEN')}"
        )
    else:
        # Polling for development
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
