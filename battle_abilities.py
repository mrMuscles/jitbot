"""
Battle Abilities System - Defines and executes all character and enemy abilities
"""
import random

# ============================================================================
# ABILITY EXECUTION ENGINE
# ============================================================================

def execute_ability(battle_state, attacker, ability_idx, targets, is_player=True):
    """
    Execute an ability based on the character and ability index
    
    Args:
        battle_state: Current battle state
        attacker: The character/enemy using the ability
        ability_idx: Index of the ability (0-3)
        targets: List of target characters/enemies
        is_player: True if attacker is a player, False if enemy
    
    Returns:
        List of log messages describing what happened
    """
    logs = []
    char_name = attacker.get("name", "Unknown")
    
    # Get ability name
    if ability_idx >= len(attacker["abilities"]):
        return ["Invalid ability!"]
    
    ability_name = attacker["abilities"][ability_idx]
    
    # Handle character-specific abilities
    if char_name.startswith("r_abraize") and not char_name.startswith("r_abraize2"):
        logs.extend(execute_r_abraize_ability(battle_state, attacker, ability_idx, targets))
    elif char_name == "r_abraize2":
        logs.extend(execute_r_abraize2_ability(battle_state, attacker, ability_idx, targets))
    elif char_name == "sr_abraize":
        logs.extend(execute_sr_abraize_ability(battle_state, attacker, ability_idx, targets))
    elif char_name == "ssr_abraize":
        logs.extend(execute_ssr_abraize_ability(battle_state, attacker, ability_idx, targets))
    elif char_name == "r_trey":
        logs.extend(execute_r_trey_ability(battle_state, attacker, ability_idx, targets))
    elif char_name == "sr_trey":
        logs.extend(execute_sr_trey_ability(battle_state, attacker, ability_idx, targets))
    elif char_name == "ssr_trey":
        logs.extend(execute_ssr_trey_ability(battle_state, attacker, ability_idx, targets))
    elif char_name == "r_noah":
        logs.extend(execute_r_noah_ability(battle_state, attacker, ability_idx, targets))
    elif char_name == "r_freeman":
        logs.extend(execute_r_freeman_ability(battle_state, attacker, ability_idx, targets))
    elif char_name == "sr_freeman":
        logs.extend(execute_sr_freeman_ability(battle_state, attacker, ability_idx, targets))
    elif char_name == "r_stephen":
        logs.extend(execute_r_stephen_ability(battle_state, attacker, ability_idx, targets))
    elif char_name == "sr_stephen":
        logs.extend(execute_sr_stephen_ability(battle_state, attacker, ability_idx, targets))
    elif char_name == "ssr_jayden":
        logs.extend(execute_ssr_jayden_ability(battle_state, attacker, ability_idx, targets))
    elif char_name == "sr_homestuck":
        logs.extend(execute_sr_homestuck_ability(battle_state, attacker, ability_idx, targets))
    elif char_name == "ssr_scottie":
        logs.extend(execute_ssr_scottie_ability(battle_state, attacker, ability_idx, targets))
    # Enemy abilities
    elif not is_player:
        logs.extend(execute_enemy_ability(battle_state, attacker, ability_idx, targets))
    else:
        # Default basic attack
        logs.extend(execute_basic_attack(battle_state, attacker, targets[0] if targets else None))
    
    return logs

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def apply_damage(battle_state, attacker, target, base_damage=None, is_true_damage=False):
    """Apply damage from attacker to target"""
    damage, hit = battle_state.calculate_damage(attacker, target, base_damage, is_true_damage)
    if hit:
        target["hp"] = max(0, target["hp"] - damage)
        if target["hp"] == 0:
            target["alive"] = False
        return damage, True
    return 0, False

def add_buff(target, buff_type, value, duration):
    """Add a buff to a target"""
    target["buffs"].append({"type": buff_type, "value": value, "duration": duration})

def add_debuff(target, debuff_type, value, duration):
    """Add a debuff to a target"""
    target["debuffs"].append({"type": debuff_type, "value": value, "duration": duration})

def get_all_allies(battle_state, is_player):
    """Get all alive allies"""
    if is_player:
        return battle_state.get_alive_players()
    else:
        return battle_state.get_alive_enemies()

def get_all_enemies(battle_state, is_player):
    """Get all alive enemies"""
    if is_player:
        return battle_state.get_alive_enemies()
    else:
        return battle_state.get_alive_players()

def execute_basic_attack(battle_state, attacker, target):
    """Execute a basic attack"""
    logs = []
    title = attacker.get("title", attacker.get("name", "Unknown"))
    target_name = target.get("title", target.get("name", "Target")) if target else "Target"
    
    if not target:
        return [f"**{title}** has no valid target!"]
    
    damage, hit = apply_damage(battle_state, attacker, target)
    if hit:
        logs.append(f"**{title}** attacked **{target_name}** for **{damage}** damage!")
        if not target["alive"]:
            logs.append(f"**{target_name}** has been defeated!")
    else:
        logs.append(f"**{title}** attacked but missed!")
    
    return logs

# ============================================================================
# CHARACTER ABILITY IMPLEMENTATIONS
# ============================================================================

def execute_r_abraize_ability(battle_state, attacker, ability_idx, targets):
    """R Abraize abilities: Punch, Sleep, Missing Assignments"""
    logs = []
    title = attacker.get("title", "R Abraize")
    
    if ability_idx == 0:  # Punch
        logs.extend(execute_basic_attack(battle_state, attacker, targets[0] if targets else None))
    elif ability_idx == 1:  # Sleep
        logs.append(f"**{title}** takes a nap!")
        # Reduce evasion to 0% for one turn, unable to act
        attacker["eva"] = 0
        # Track sleeping state (1 turn of sleep)
        attacker["special_states"]["sleeping"] = 1
        # After waking up, apply buff for 2 turns
        attacker["special_states"]["sleep_buff_pending"] = 2
    elif ability_idx == 2:  # Missing Assignments
        logs.append(f"**{title}** completes missing assignments!")
        add_buff(attacker, "acc", 0.05, 1)
    
    return logs

def execute_r_abraize2_ability(battle_state, attacker, ability_idx, targets):
    """R Abraize2 abilities: Punch, Eat Note, Productivity Time"""
    logs = []
    title = attacker.get("title", "R Abraize2")
    
    if ability_idx == 0:  # Punch
        logs.extend(execute_basic_attack(battle_state, attacker, targets[0] if targets else None))
    elif ability_idx == 1:  # Eat Note
        attacker["hp"] = max(1, attacker["hp"] - 25)
        add_buff(attacker, "eva", 0.10, 1)
        logs.append(f"**{title}** eats a note! Lost 25 HP but gained evasion!")
    elif ability_idx == 2:  # Productivity Time
        logs.append(f"**{title}** enters productivity time!")
        for ally in get_all_allies(battle_state, True):
            add_buff(ally, "atk", 0.10, 3)
            add_buff(ally, "def", 0.10, 3)
        attacker["cooldowns"][2] = 4
    
    return logs

def execute_sr_abraize_ability(battle_state, attacker, ability_idx, targets):
    """SR Abraize abilities: Punch, Slow, Attempt"""
    logs = []
    title = attacker.get("title", "SR Abraize")
    
    if ability_idx == 0:  # Punch
        logs.extend(execute_basic_attack(battle_state, attacker, targets[0] if targets else None))
    elif ability_idx == 1:  # Slow
        if targets:
            add_debuff(targets[0], "acc", 0.15, 1)
            logs.append(f"**{title}** slows **{targets[0].get('name', 'enemy')}**!")
    elif ability_idx == 2:  # Attempt
        roll = random.random()
        if roll < 0.15:  # 15% success
            logs.append(f"**{title}** successfully travels back in time!")
            # Heal 50%
            heal_amount = int(attacker["max_hp"] * 0.5)
            attacker["hp"] = min(attacker["max_hp"], attacker["hp"] + heal_amount)
            # Buff all allies
            for ally in get_all_allies(battle_state, True):
                add_buff(ally, "atk", 0.20, 1)
        else:
            logs.append(f"**{title}** attempts to travel back in time... but nothing happens!")
    
    return logs

def execute_ssr_abraize_ability(battle_state, attacker, ability_idx, targets):
    """SSR Abraize abilities: Accelerated Punch, Fast Forward, Rewind, Universal Stabilizer"""
    logs = []
    title = attacker.get("title", "SSR Abraize")
    
    if ability_idx == 0:  # Accelerated Punch
        # Guaranteed hit
        if targets:
            target = targets[0]
            # Get accelerated stacks
            stacks = attacker["special_states"].get("accelerated", 0)
            bonus = min(1.0, stacks * 0.10)  # Max 100%
            
            damage = int(attacker["atk"] * (1 + bonus))
            target["hp"] = max(0, target["hp"] - damage)
            if target["hp"] == 0:
                target["alive"] = False
            
            logs.append(f"**{title}** uses Accelerated Punch on **{target.get('name', 'enemy')}** for **{damage}** damage!")
            
            # Add stack
            attacker["special_states"]["accelerated"] = stacks + 1
            if not target["alive"]:
                logs.append(f"**{target.get('name', 'enemy')}** has been defeated!")
    elif ability_idx == 1:  # Fast Forward
        logs.append(f"**{title}** fast forwards!")
        for ally in get_all_allies(battle_state, True):
            add_buff(ally, "acc", 0.05, 1)
            add_buff(ally, "atk", 0.40, 1)
            add_buff(ally, "def", 0.15, 1)
        # Grant extra turn (simplified - just logs it)
        logs.append(f"**{title}** can act again this turn!")
        attacker["cooldowns"][1] = 5
    elif ability_idx == 2:  # Rewind
        logs.append(f"**{title}** rewinds time! (Stats reverted to previous turn)")
        # Simplified implementation
        attacker["cooldowns"][2] = 2
    elif ability_idx == 3:  # Universal Stabilizer (Ultimate)
        logs.append(f"**{title}** activates Universal Stabilizer!")
        for ally in get_all_allies(battle_state, True):
            add_buff(ally, "atk", 0.50, 5)
            ally["special_states"]["debuff_immunity"] = 5
            ally["hp"] = ally["max_hp"]  # Full heal
        attacker["cooldowns"][3] = 999  # Cannot be used again
    
    return logs

def execute_r_trey_ability(battle_state, attacker, ability_idx, targets):
    """R Trey abilities: Punch, Irish Goodbye, Cheesy Fries"""
    logs = []
    title = attacker.get("title", "R Trey")
    
    if ability_idx == 0:  # Punch
        logs.extend(execute_basic_attack(battle_state, attacker, targets[0] if targets else None))
    elif ability_idx == 1:  # Irish Goodbye
        add_buff(attacker, "eva", 0.10, 1)
        attacker["cooldowns"][1] = 2
        logs.append(f"**{title}** performs an Irish Goodbye!")
    elif ability_idx == 2:  # Cheesy Fries
        if targets and random.random() < 0.70:  # 70% hit chance
            target = targets[0]
            # Apply burn (simplified as damage over time)
            target["special_states"]["burn"] = 1
            logs.append(f"**{title}** throws cheesy fries at **{target.get('name', 'enemy')}**! They're burning!")
        else:
            logs.append(f"**{title}** throws cheesy fries but misses!")
    
    return logs

def execute_sr_trey_ability(battle_state, attacker, ability_idx, targets):
    """SR Trey abilities: Punch, Drowsy, Whispers from Beyond"""
    logs = []
    title = attacker.get("title", "SR Trey")
    
    if ability_idx == 0:  # Punch
        logs.extend(execute_basic_attack(battle_state, attacker, targets[0] if targets else None))
    elif ability_idx == 1:  # Drowsy
        for enemy in get_all_enemies(battle_state, True):
            add_debuff(enemy, "acc", 0.10, 1)
        logs.append(f"**{title}** makes all enemies drowsy!")
    elif ability_idx == 2:  # Whispers from Beyond
        for ally in get_all_allies(battle_state, True):
            add_buff(ally, "acc", 0.10, 1)
        logs.append(f"**{title}** hears whispers from beyond!")
    
    return logs

def execute_ssr_trey_ability(battle_state, attacker, ability_idx, targets):
    """SSR Trey abilities: Punch, Cloak and Dagger, Shroud, Reality Sink"""
    logs = []
    title = attacker.get("title", "SSR Trey")
    
    if ability_idx == 0:  # Punch
        logs.extend(execute_basic_attack(battle_state, attacker, targets[0] if targets else None))
    elif ability_idx == 1:  # Cloak and Dagger
        add_buff(attacker, "eva", 1.0, 1)  # 100% evasion
        add_buff(attacker, "acc", 0.10, 1)
        if targets:
            target = targets[0]
            true_damage = int(target["max_hp"] * 0.10)
            target["hp"] = max(0, target["hp"] - true_damage)
            if target["hp"] == 0:
                target["alive"] = False
            logs.append(f"**{title}** stabs **{target.get('name', 'enemy')}** for **{true_damage}** true damage!")
            if not target["alive"]:
                logs.append(f"**{target.get('name', 'enemy')}** has been defeated!")
        attacker["cooldowns"][1] = 2
    elif ability_idx == 2:  # Shroud
        for ally in get_all_allies(battle_state, True):
            add_buff(ally, "eva", 0.50, 3)
        attacker["special_states"]["taunt"] = 1
        logs.append(f"**{title}** shrouds allies in void and draws enemy attacks!")
        attacker["cooldowns"][2] = 4
    elif ability_idx == 3:  # Reality Sink (Ultimate)
        battle_state.special_states["void_spot"] = {
            "turns": 3,
            "power": 0,
            "owner": attacker
        }
        logs.append(f"**{title}** creates a void spot! Ranged attacks will miss for 3 turns!")
        attacker["cooldowns"][3] = 999
    
    return logs

def execute_r_noah_ability(battle_state, attacker, ability_idx, targets):
    """R Noah abilities: Punch, Fiddle, Bo"""
    logs = []
    title = attacker.get("title", "R Noah")
    
    if ability_idx == 0:  # Punch
        logs.extend(execute_basic_attack(battle_state, attacker, targets[0] if targets else None))
    elif ability_idx == 1:  # Fiddle
        if targets:
            add_debuff(targets[0], "acc", 0.05, 1)
            logs.append(f"**{title}** sends an annoying text to **{targets[0].get('name', 'enemy')}**!")
    elif ability_idx == 2:  # Bo
        attacker["special_states"]["interfere"] = 1
        attacker["cooldowns"][2] = 2
        logs.append(f"**{title}** prepares to interfere!")
    
    return logs

def execute_r_freeman_ability(battle_state, attacker, ability_idx, targets):
    """R Freeman abilities: Slap, Ponder, SMASH!"""
    logs = []
    title = attacker.get("title", "R Freeman")
    
    if ability_idx == 0:  # Slap
        logs.extend(execute_basic_attack(battle_state, attacker, targets[0] if targets else None))
    elif ability_idx == 1:  # Ponder
        for ally in get_all_allies(battle_state, True):
            add_buff(ally, "eva", 0.03, 1)
        logs.append(f"**{title}** ponders, boosting ally evasion!")
    elif ability_idx == 2:  # SMASH!
        if targets:
            add_buff(attacker, "atk", 0.10, 0)  # Temporary for this attack
            damage, hit = apply_damage(battle_state, attacker, targets[0])
            if hit:
                attacker["hp"] = max(1, attacker["hp"] - damage)  # Take recoil damage
                logs.append(f"**{title}** SMASHES **{targets[0].get('name', 'enemy')}** for **{damage}** damage but takes {damage} recoil!")
                if not targets[0]["alive"]:
                    logs.append(f"**{targets[0].get('name', 'enemy')}** has been defeated!")
            else:
                logs.append(f"**{title}** tries to SMASH but misses!")
    
    return logs

def execute_sr_freeman_ability(battle_state, attacker, ability_idx, targets):
    """SR Freeman abilities: Pistol Whip, Shoot, Hide"""
    logs = []
    title = attacker.get("title", "SR Freeman")
    
    if ability_idx == 0:  # Pistol Whip
        logs.extend(execute_basic_attack(battle_state, attacker, targets[0] if targets else None))
    elif ability_idx == 1:  # Shoot
        # SR Freeman's Shoot ability: 80% safety on (no damage), 20% safety off (10% current HP damage)
        if targets and random.random() < 0.20:  # 20% safety off
            damage = int(targets[0]["hp"] * 0.10)
            targets[0]["hp"] = max(0, targets[0]["hp"] - damage)
            if targets[0]["hp"] == 0:
                targets[0]["alive"] = False
            logs.append(f"**{title}** shoots **{targets[0].get('name', 'enemy')}** for **{damage}** damage!")
            if not targets[0]["alive"]:
                logs.append(f"**{targets[0].get('name', 'enemy')}** has been defeated!")
        else:
            logs.append(f"**{title}** pulls the trigger but the safety was on!")
    elif ability_idx == 2:  # Hide
        attacker["special_states"]["nervous"] = 999  # Permanent until used
        logs.append(f"**{title}** hides nervously!")
    
    return logs

def execute_r_stephen_ability(battle_state, attacker, ability_idx, targets):
    """R Stephen abilities: Dropkick, Light up, Lock the fuck in"""
    logs = []
    title = attacker.get("title", "R Stephen")
    
    if ability_idx == 0:  # Dropkick
        logs.extend(execute_basic_attack(battle_state, attacker, targets[0] if targets else None))
    elif ability_idx == 1:  # Light up
        attacker["special_states"]["baller"] = attacker["special_states"].get("baller", 0) + 3
        logs.append(f"**{title}** lights a BALLER cigarette!")
    elif ability_idx == 2:  # Lock the fuck in
        stacks = attacker["special_states"].get("baller", 0)
        add_buff(attacker, "atk", 0.05 * stacks, 1)
        logs.append(f"**{title}** locks in with {stacks} BALLER stacks!")
    
    return logs

def execute_sr_stephen_ability(battle_state, attacker, ability_idx, targets):
    """SR Stephen abilities: Dropkick, Consider Intervening, HIYAAAHHH!"""
    logs = []
    title = attacker.get("title", "SR Stephen")
    
    if ability_idx == 0:  # Dropkick
        logs.extend(execute_basic_attack(battle_state, attacker, targets[0] if targets else None))
    elif ability_idx == 1:  # Consider Intervening
        attacker["special_states"]["considering"] = attacker["special_states"].get("considering", 0) + 1
        # Set expiration
        attacker["special_states"]["considering_turns"] = 3
        logs.append(f"**{title}** considers intervening...")
    elif ability_idx == 2:  # HIYAAAHHH!
        stacks = attacker["special_states"].get("considering", 0)
        if targets:
            bonus = stacks * 0.10
            old_atk = attacker["atk"]
            attacker["atk"] = int(attacker["base_atk"] * (1 + bonus))
            damage, hit = apply_damage(battle_state, attacker, targets[0])
            attacker["atk"] = old_atk
            if hit:
                logs.append(f"**{title}** HIYAAAHHH! Hits **{targets[0].get('name', 'enemy')}** for **{damage}** damage with {stacks} stacks!")
                if not targets[0]["alive"]:
                    logs.append(f"**{targets[0].get('name', 'enemy')}** has been defeated!")
            else:
                logs.append(f"**{title}** HIYAAAHHH! But misses!")
        attacker["special_states"]["considering"] = 0
    
    return logs

def execute_ssr_jayden_ability(battle_state, attacker, ability_idx, targets):
    """SSR Jayden abilities: Punch, Butler of Swatabi, Indecision, Genesis"""
    logs = []
    title = attacker.get("title", "SSR Jayden")
    
    if ability_idx == 0:  # Punch
        logs.extend(execute_basic_attack(battle_state, attacker, targets[0] if targets else None))
    elif ability_idx == 1:  # Butler of Swatabi
        for enemy in get_all_enemies(battle_state, True):
            add_debuff(enemy, "acc", 0.30, 1)
        logs.append(f"**{title}** leverages their dreadful reputation!")
    elif ability_idx == 2:  # Indecision
        roll = random.random()
        if roll < 0.33:  # Buff allies
            for ally in get_all_allies(battle_state, True):
                add_buff(ally, "atk", 0.20, 1)
                add_buff(ally, "def", 0.20, 1)
            logs.append(f"**{title}** buffs all allies!")
        elif roll < 0.66:  # Debuff enemies
            for enemy in get_all_enemies(battle_state, True):
                add_debuff(enemy, "atk", 0.20, 1)
                add_debuff(enemy, "def", 0.20, 1)
            logs.append(f"**{title}** debuffs all enemies!")
        else:  # Damage self
            attacker["hp"] = max(1, attacker["hp"] - 1)
            logs.append(f"**{title}** indecisively hurts themselves for 1 damage!")
    elif ability_idx == 3:  # Genesis (Ultimate)
        for ally in get_all_allies(battle_state, True):
            ally["special_states"]["regeneration"] = 7
        for enemy in get_all_enemies(battle_state, True):
            add_debuff(enemy, "acc", 0.25, 7)
            enemy["max_hp"] = int(enemy["max_hp"] * 0.65)  # Reduce max HP by 35%
            enemy["hp"] = min(enemy["hp"], enemy["max_hp"])
            add_debuff(enemy, "def", 0.25, 7)
        logs.append(f"**{title}** unleashes Genesis! Allies regenerate, enemies are warped!")
        attacker["cooldowns"][3] = 999
    
    return logs

def execute_sr_homestuck_ability(battle_state, attacker, ability_idx, targets):
    """SR Homestuck abilities: Impractical Assailants, Plunder, Thief"""
    logs = []
    title = attacker.get("title", "SR Homestuck")
    
    if ability_idx == 0:  # Impractical Assailants (die roll)
        if targets:
            die_roll = random.randint(1, 6)
            damage = die_roll * 10
            targets[0]["hp"] = max(0, targets[0]["hp"] - damage)
            if targets[0]["hp"] == 0:
                targets[0]["alive"] = False
            logs.append(f"**{title}** rolls a {die_roll}! Deals **{damage}** damage to **{targets[0].get('name', 'enemy')}**!")
            if not targets[0]["alive"]:
                logs.append(f"**{targets[0].get('name', 'enemy')}** has been defeated!")
    elif ability_idx == 1:  # Plunder
        allies = get_all_allies(battle_state, True)
        if len(allies) > 1:
            victim = random.choice([a for a in allies if a != attacker])
            add_debuff(victim, "atk", 0.15, 1)
            add_buff(attacker, "atk", 0.15, 1)
            logs.append(f"**{title}** plunders from **{victim.get('title', 'ally')}**!")
    elif ability_idx == 2:  # Thief
        for enemy in get_all_enemies(battle_state, True):
            add_debuff(enemy, "acc", 1.0, 1)  # -100% acc
        for ally in get_all_allies(battle_state, True):
            add_buff(ally, "acc", 1.0, 1)  # +100% acc (capped)
        logs.append(f"**{title}** steals accuracy from enemies!")
        attacker["cooldowns"][2] = 5
    
    return logs

def execute_ssr_scottie_ability(battle_state, attacker, ability_idx, targets):
    """SSR Scottie abilities: Shield Bash, Guardian's Shield, Fortify, Eternal Watch"""
    logs = []
    title = attacker.get("title", "SSR Scottie")
    
    if ability_idx == 0:  # Shield Bash
        if targets:
            damage, hit = apply_damage(battle_state, attacker, targets[0])
            if hit:
                logs.append(f"**{title}** shield bashes **{targets[0].get('name', 'enemy')}** for **{damage}** damage!")
                if random.random() < 0.20:  # 20% stun chance
                    targets[0]["special_states"]["stunned"] = 1
                    logs.append(f"**{targets[0].get('name', 'enemy')}** is stunned!")
                if not targets[0]["alive"]:
                    logs.append(f"**{targets[0].get('name', 'enemy')}** has been defeated!")
            else:
                logs.append(f"**{title}** shield bashes but misses!")
    elif ability_idx == 1:  # Guardian's Shield
        shield_amount = int(attacker["max_hp"] * 0.20)
        for ally in get_all_allies(battle_state, True):
            ally["special_states"]["shield"] = shield_amount
            ally["special_states"]["shield_duration"] = 3
        logs.append(f"**{title}** creates shields for all allies!")
        attacker["cooldowns"][1] = 4
    elif ability_idx == 2:  # Fortify
        for ally in get_all_allies(battle_state, True):
            add_buff(ally, "def", 0.30, 3)
        logs.append(f"**{title}** fortifies all allies!")
        attacker["cooldowns"][2] = 4
    elif ability_idx == 3:  # Eternal Watch (Ultimate)
        for ally in get_all_allies(battle_state, True):
            add_buff(ally, "def", 0.50, 2)
            ally["special_states"]["damage_immunity"] = 2
            ally["hp"] = ally["max_hp"]
        logs.append(f"**{title}** assumes the role of eternal guardian! All allies are protected!")
        attacker["cooldowns"][3] = 999
    
    return logs

# ============================================================================
# ENEMY ABILITY IMPLEMENTATIONS
# ============================================================================

def execute_enemy_ability(battle_state, enemy, ability_idx, targets):
    """Execute enemy abilities"""
    logs = []
    enemy_name = enemy.get("name", "Enemy")
    
    if not targets:
        return [f"**{enemy_name}** has no valid target!"]
    
    target = targets[0]
    
    # Most enemies just do basic attacks with variations
    if ability_idx == 0:  # Basic attack
        logs.extend(execute_basic_attack(battle_state, enemy, target))
    elif enemy.get("type") == "Grunt" and ability_idx == 1:  # Slam
        # Grunt's Slam ability deals flat 15 damage to all party members
        GRUNT_SLAM_DAMAGE = 15
        for player in get_all_allies(battle_state, False):
            player["hp"] = max(0, player["hp"] - GRUNT_SLAM_DAMAGE)
            if player["hp"] == 0:
                player["alive"] = False
        logs.append(f"**{enemy_name}** uses Slam! All players take {GRUNT_SLAM_DAMAGE} damage!")
    elif enemy.get("type") == "Spearman":
        if ability_idx == 1:  # Swipe
            for player in get_all_allies(battle_state, False):
                damage, hit = apply_damage(battle_state, enemy, player)
                if hit:
                    logs.append(f"**{enemy_name}** swipes **{player.get('title', 'player')}** for **{damage}** damage!")
        elif ability_idx == 2:  # Stab
            add_buff(enemy, "atk", 0.15, 0)  # This turn only
            damage, hit = apply_damage(battle_state, enemy, target)
            if hit:
                logs.append(f"**{enemy_name}** stabs **{target.get('title', 'player')}** for **{damage}** damage!")
    elif enemy.get("type") == "Agent" and ability_idx == 1:  # Sneak
        add_buff(enemy, "eva", 0.15, 1)
        logs.append(f"**{enemy_name}** sneaks into the shadows!")
    elif enemy.get("type") == "Jack Noir":
        if ability_idx == 0:  # Stab
            logs.extend(execute_basic_attack(battle_state, enemy, target))
        elif ability_idx == 1:  # Shiv
            damage, hit = apply_damage(battle_state, enemy, target)
            if hit:
                target["special_states"]["bleed"] = target["special_states"].get("bleed", 0) + 1
                logs.append(f"**{enemy_name}** shivs **{target.get('title', 'player')}** for **{damage}** damage! Bleeding!")
        elif ability_idx == 2:  # Slash
            for player in get_all_allies(battle_state, False):
                player["hp"] = max(0, player["hp"] - 5)
                player["special_states"]["bleed"] = player["special_states"].get("bleed", 0) + 1
                if player["hp"] == 0:
                    player["alive"] = False
            logs.append(f"**{enemy_name}** slashes all players for 5 damage and applies bleed!")
    else:
        # Default to basic attack
        logs.extend(execute_basic_attack(battle_state, enemy, target))
    
    return logs
