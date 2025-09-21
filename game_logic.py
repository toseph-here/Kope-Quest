"""
Game Logic for Telegram RPG Bot
Contains core game mechanics, combat system, and player/NPC classes
"""

import random
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class Player:
    """Player class representing a player character"""
    user_id: int
    username: str
    element: str
    level: int
    experience: int
    hp: int
    max_hp: int
    stamina: int
    max_stamina: int
    attack: int
    defense: int
    agility: int
    element_power: int
    coins: int = 0
    battles_won: int = 0
    battles_lost: int = 0

    def __init__(self, player_data: Dict[str, Any]):
        """Initialize player from database data"""
        self.user_id = player_data['user_id']
        self.username = player_data['username']
        self.element = player_data['element']
        self.level = player_data['level']
        self.experience = player_data['experience']
        self.hp = player_data['hp']
        self.max_hp = player_data['max_hp']
        self.stamina = player_data['stamina']
        self.max_stamina = player_data['max_stamina']
        self.attack = player_data['attack']
        self.defense = player_data['defense']
        self.agility = player_data['agility']
        self.element_power = player_data['element_power']
        self.coins = player_data.get('coins', 0)
        self.battles_won = player_data.get('battles_won', 0)
        self.battles_lost = player_data.get('battles_lost', 0)

    def is_alive(self) -> bool:
        """Check if player is still alive"""
        return self.hp > 0

    def can_use_element_skill(self) -> bool:
        """Check if player has enough stamina for element skill"""
        return self.stamina >= 15

    def can_heal(self) -> bool:
        """Check if player can heal"""
        return self.stamina >= 10 and self.hp < self.max_hp


@dataclass
class NPC:
    """NPC class representing computer-controlled enemies"""
    name: str
    element: str
    level: int
    hp: int
    max_hp: int
    stamina: int
    max_stamina: int
    attack: int
    defense: int
    agility: int
    element_power: int

    def is_alive(self) -> bool:
        """Check if NPC is still alive"""
        return self.hp > 0

    def can_use_element_skill(self) -> bool:
        """Check if NPC has enough stamina for element skill"""
        return self.stamina >= 15

    def can_heal(self) -> bool:
        """Check if NPC can heal"""
        return self.stamina >= 10 and self.hp < self.max_hp


class GameLogic:
    """Core game logic and mechanics"""

    def __init__(self):
        # Element effectiveness matrix
        self.element_effectiveness = {
            'Fire': {'Ice': 1.5, 'Earth': 0.8, 'Water': 0.8},
            'Ice': {'Water': 1.5, 'Fire': 0.8, 'Lightning': 0.8},
            'Lightning': {'Water': 1.5, 'Ice': 0.8, 'Earth': 1.5},
            'Water': {'Fire': 1.5, 'Lightning': 0.8, 'Wind': 0.8},
            'Earth': {'Lightning': 1.5, 'Wind': 1.5, 'Fire': 0.8},
            'Wind': {'Earth': 0.8, 'Shadow': 1.5, 'Water': 1.5},
            'Shadow': {'Light': 1.5, 'Wind': 0.8, 'Fire': 1.2},
            'Light': {'Shadow': 1.5, 'Fire': 1.2, 'Ice': 1.2}
        }

    def get_element_effectiveness(self, attacker_element: str, defender_element: str) -> float:
        """Get element effectiveness multiplier"""
        if attacker_element in self.element_effectiveness:
            return self.element_effectiveness[attacker_element].get(defender_element, 1.0)
        return 1.0

    def calculate_damage(self, attacker, defender, action: str = 'attack', is_critical: bool = False) -> int:
        """Calculate damage dealt in combat"""
        base_damage = 0

        if action == 'attack':
            base_damage = attacker.attack
        elif action == 'element':
            base_damage = attacker.element_power
        else:
            return 0

        # Apply defense
        defense_reduction = defender.defense * 0.5
        damage = max(1, base_damage - defense_reduction)

        # Element effectiveness
        if action == 'element':
            effectiveness = self.get_element_effectiveness(attacker.element, defender.element)
            damage *= effectiveness

        # Random variance (80% - 120%)
        variance = random.uniform(0.8, 1.2)
        damage *= variance

        # Critical hit
        if is_critical:
            damage *= 1.5

        return max(1, int(damage))

    def check_critical_hit(self, attacker) -> bool:
        """Check if attack is a critical hit (10% base chance + agility bonus)"""
        base_crit_chance = 0.1
        agility_bonus = attacker.agility * 0.001  # 1% per 10 agility
        total_crit_chance = min(0.3, base_crit_chance + agility_bonus)  # Max 30%

        return random.random() < total_crit_chance

    def create_npc(self, enemy_type: str, level: int, location_element: str) -> NPC:
        """Create an NPC enemy"""
        # Base stats scale with level
        base_hp = 80 + (level * 8)
        base_stamina = 40 + (level * 4)
        base_attack = 20 + (level * 3)
        base_defense = 15 + (level * 2)
        base_agility = 10 + (level * 2)
        base_element_power = 25 + (level * 3)

        # Element-specific names and bonuses
        element_names = {
            'Fire': ['Flame Sprite', 'Fire Elemental', 'Inferno Beast', 'Lava Golem'],
            'Ice': ['Frost Wolf', 'Ice Shard', 'Frozen Warrior', 'Blizzard Spirit'],
            'Lightning': ['Storm Eagle', 'Thunder Beast', 'Lightning Wisp', 'Electric Drake'],
            'Water': ['Water Nymph', 'Tide Guardian', 'Aqua Serpent', 'Ocean Spirit'],
            'Earth': ['Stone Golem', 'Rock Crusher', 'Earth Shaker', 'Mountain Bear'],
            'Wind': ['Wind Dancer', 'Gale Force', 'Sky Hunter', 'Tornado Spirit'],
            'Shadow': ['Shadow Wraith', 'Dark Assassin', 'Void Stalker', 'Nightmare'],
            'Light': ['Light Guardian', 'Solar Warrior', 'Divine Beast', 'Radiance']
        }

        # Choose random name for the element
        names = element_names.get(location_element, ['Unknown Enemy'])
        enemy_name = random.choice(names)

        # Add some randomness to stats (±15%)
        stat_variance = random.uniform(0.85, 1.15)

        npc = NPC(
            name=enemy_name,
            element=location_element,
            level=level,
            hp=int(base_hp * stat_variance),
            max_hp=int(base_hp * stat_variance),
            stamina=int(base_stamina * stat_variance),
            max_stamina=int(base_stamina * stat_variance),
            attack=int(base_attack * stat_variance),
            defense=int(base_defense * stat_variance),
            agility=int(base_agility * stat_variance),
            element_power=int(base_element_power * stat_variance)
        )

        return npc

    async def execute_battle_action(self, actor, target, action: str) -> Dict[str, Any]:
        """Execute a battle action and return results"""
        action_log = ""
        winner = None

        try:
            if action == 'attack':
                # Normal attack
                is_critical = self.check_critical_hit(actor)
                damage = self.calculate_damage(actor, target, 'attack', is_critical)
                target.hp = max(0, target.hp - damage)

                crit_text = " 💥 CRITICAL HIT!" if is_critical else ""
                action_log = f"{actor.name if hasattr(actor, 'name') else actor.username} attacks for {damage} damage!{crit_text}"

            elif action == 'defend':
                # Defend action - reduce incoming damage next turn and restore stamina
                stamina_restore = min(5, actor.max_stamina - actor.stamina)
                actor.stamina = min(actor.max_stamina, actor.stamina + stamina_restore)
                action_log = f"{actor.name if hasattr(actor, 'name') else actor.username} takes a defensive stance and recovers {stamina_restore} stamina!"

            elif action == 'heal':
                # Heal action - costs stamina
                if actor.can_heal():
                    stamina_cost = 10
                    heal_amount = min(actor.level * 8 + 15, actor.max_hp - actor.hp)

                    actor.hp = min(actor.max_hp, actor.hp + heal_amount)
                    actor.stamina = max(0, actor.stamina - stamina_cost)

                    action_log = f"{actor.name if hasattr(actor, 'name') else actor.username} heals for {heal_amount} HP!"
                else:
                    action_log = f"{actor.name if hasattr(actor, 'name') else actor.username} cannot heal right now!"

            elif action == 'element':
                # Element skill - powerful attack that costs stamina
                if actor.can_use_element_skill():
                    stamina_cost = 15
                    is_critical = self.check_critical_hit(actor)
                    damage = self.calculate_damage(actor, target, 'element', is_critical)
                    target.hp = max(0, target.hp - damage)
                    actor.stamina = max(0, actor.stamina - stamina_cost)

                    effectiveness = self.get_element_effectiveness(actor.element, target.element)
                    effectiveness_text = ""
                    if effectiveness > 1.0:
                        effectiveness_text = " ⚡ It's super effective!"
                    elif effectiveness < 1.0:
                        effectiveness_text = " 🛡️ It's not very effective..."

                    crit_text = " 💥 CRITICAL HIT!" if is_critical else ""

                    action_log = (f"{actor.name if hasattr(actor, 'name') else actor.username} uses {actor.element} skill for {damage} damage!"
                                f"{effectiveness_text}{crit_text}")
                else:
                    action_log = f"{actor.name if hasattr(actor, 'name') else actor.username} doesn't have enough stamina for element skill!"

            # Check if target is defeated
            if not target.is_alive():
                winner = 'player' if hasattr(actor, 'user_id') else 'npc'
                action_log += f"\n\n💀 {target.name if hasattr(target, 'name') else target.username} has been defeated!"

            return {
                'log': action_log,
                'winner': winner,
                'damage_dealt': 0  # Could track this for statistics
            }

        except Exception as e:
            logger.error(f"Error executing battle action: {e}")
            return {
                'log': "⚠️ An error occurred during the action.",
                'winner': None,
                'damage_dealt': 0
            }

    def choose_npc_action(self, npc: NPC, target) -> str:
        """Choose action for NPC based on AI logic"""
        try:
            # Simple AI logic
            hp_percentage = npc.hp / npc.max_hp
            stamina_percentage = npc.stamina / npc.max_stamina

            # If low HP and can heal, prioritize healing
            if hp_percentage < 0.3 and npc.can_heal():
                return 'heal'

            # If high stamina and element skill available, use it
            if stamina_percentage > 0.6 and npc.can_use_element_skill():
                # Check element effectiveness
                effectiveness = self.get_element_effectiveness(npc.element, target.element)
                if effectiveness >= 1.0:  # Use if neutral or effective
                    return 'element'

            # If low stamina, defend to recover
            if stamina_percentage < 0.3:
                return 'defend'

            # Random choice weighted towards attack
            actions = ['attack', 'attack', 'attack', 'defend']
            return random.choice(actions)

        except Exception as e:
            logger.error(f"Error choosing NPC action: {e}")
            return 'attack'  # Default to attack

    def calculate_xp_reward(self, player_level: int, enemy_level: int) -> int:
        """Calculate XP reward based on level difference"""
        base_xp = enemy_level * 20
        level_diff = enemy_level - player_level

        # Bonus for fighting higher level enemies
        if level_diff > 0:
            bonus_multiplier = 1 + (level_diff * 0.15)
        # Penalty for fighting much lower level enemies
        elif level_diff < -5:
            bonus_multiplier = max(0.1, 1 + (level_diff * 0.1))
        else:
            bonus_multiplier = 1.0

        return max(1, int(base_xp * bonus_multiplier))

    def calculate_coin_reward(self, player_level: int, enemy_level: int) -> int:
        """Calculate coin reward based on level difference"""
        base_coins = enemy_level * 10
        level_diff = enemy_level - player_level

        # Similar to XP but slightly different scaling
        if level_diff > 0:
            bonus_multiplier = 1 + (level_diff * 0.1)
        elif level_diff < -5:
            bonus_multiplier = max(0.2, 1 + (level_diff * 0.05))
        else:
            bonus_multiplier = 1.0

        return max(1, int(base_coins * bonus_multiplier))

    def check_level_up(self, current_xp: int, current_level: int) -> Optional[int]:
        """Check if player should level up and return new level"""
        xp_for_next_level = (current_level ** 2) * 100

        if current_xp >= xp_for_next_level:
            # Calculate new level
            new_level = current_level + 1
            return new_level

        return None

    def get_player_power_rating(self, player_data: Dict[str, Any]) -> int:
        """Calculate overall power rating for matchmaking"""
        level = player_data['level']
        total_stats = (player_data['attack'] + player_data['defense'] + 
                      player_data['agility'] + player_data['element_power'])

        # Simple power rating calculation
        return (level * 50) + total_stats

    def simulate_auto_battle(self, player1, player2) -> Dict[str, Any]:
        """Simulate a quick auto-battle between two entities"""
        # This could be used for tournament systems or quick PvP
        battle_log = []
        turn = 1

        while player1.is_alive() and player2.is_alive() and turn <= 20:  # Max 20 turns
            # Player 1's turn
            if player1.is_alive():
                action = self.choose_npc_action(player1, player2)
                result = asyncio.run(self.execute_battle_action(player1, player2, action))
                battle_log.append(f"Turn {turn}: {result['log']}")

                if result['winner']:
                    break

            # Player 2's turn
            if player2.is_alive():
                action = self.choose_npc_action(player2, player1)
                result = asyncio.run(self.execute_battle_action(player2, player1, action))
                battle_log.append(f"Turn {turn}: {result['log']}")

                if result['winner']:
                    break

            turn += 1

        # Determine winner
        if not player1.is_alive():
            winner = 'player2'
        elif not player2.is_alive():
            winner = 'player1'
        else:
            # Draw - winner is whoever has more HP percentage
            p1_hp_pct = player1.hp / player1.max_hp
            p2_hp_pct = player2.hp / player2.max_hp
            winner = 'player1' if p1_hp_pct > p2_hp_pct else 'player2'

        return {
            'winner': winner,
            'battle_log': battle_log,
            'turns': turn
  }
