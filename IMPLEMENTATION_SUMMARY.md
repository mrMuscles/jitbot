# Battle System Implementation Summary

## Overview
This implementation adds a complete attribute calculation system and enemy attack mechanics to the Discord bot's battle system.

## Key Features

### 1. Battle State Management
The `BattleView` class now maintains comprehensive state for all participants:

**Player State:**
- Base attributes (HP, ATK, DEF, EVA, ACC)
- Current EHP (Effective Health Points)
- Total EHP for calculating display HP
- Rarity multiplier (R=1, SR=1.5, SSR=2)
- Alive status
- Buffs and debuffs with durations

**Enemy State:**
- Base attributes (HP, ATK, DEF, EVA, ACC)
- Current HP (enemies don't use EHP system)
- Total HP
- Alive status
- Buffs and debuffs with durations
- Available abilities

### 2. EHP (Effective Health Points) System

The EHP system implements the "Effective Health" calculation as specified:

**Formula:**
```
Total EHP = HP + (DEF × Rarity Multiplier)
```

**Rarity Multipliers:**
- R rank: 1.0
- SR rank: 1.5
- SSR rank: 2.0

**Example (from requirements):**
- HP: 50, DEF: 10, Rank: SSR (multiplier = 2)
- Total EHP: 50 + (10 × 2) = 70
- After 20 damage: Current EHP = 50
- Displayed HP: (50/70) × 50 = 35.7 → 36 HP (rounded up)

**Displayed HP Calculation:**
```python
ratio = current_ehp / total_ehp
displayed_hp = round_up(ratio × total_hp)
```

### 3. Combat System

**Attack Resolution Order:**
1. **Accuracy Check**: Roll against attacker's ACC stat
   - If fails → attack misses (no evasion roll)
2. **Evasion Check**: (Only if accuracy succeeds) Roll against defender's EVA stat
   - If succeeds → attack dodged
3. **Damage Application**: Apply damage to defender's EHP

**Buffs/Debuffs:**
- Stored in dictionaries with `{name: {value: float, duration: int}}`
- Applied to stats during calculations
- Durations decremented each turn
- Expired buffs/debuffs removed automatically

### 4. Enemy AI

**Ability Selection:**
- Randomly chooses from available abilities (excluding passive descriptions)
- Equal probability for all abilities

**Target Selection:**
- **Single Target**: Random alive player
- **AOE**: All alive players

**Implemented Enemies:**
- ✓ Ruffian (can spawn 1 or 2, 50% chance each)
- ✓ Grunt
- ✓ Spearman
- ✓ Agent
- ✗ Jack Noir (excluded per requirements)

### 5. Death and Removal

**Player Death:**
- HP reaches 0 → player marked as dead
- Player removed from battle_screen.png
- Player skipped in turn order
- If all players dead → Enemy wins, battle ends

**Enemy Death:**
- Currently only matters for Ruffian spawns
- Enemy removed from battle_screen.png when HP reaches 0
- Framework ready for player attacks (not yet implemented)

### 6. HP Display

Added to battle embed as a field showing:
```
**Players:**
[Character Name]: XX/YY HP
[Dead Character]: ☠️ DEAD

**Enemies:**
[Enemy Name]: XX/YY HP
```

Easy to modify display format by editing `create_hp_display()` method.

### 7. Battle Flow

**Turn Order:**
1. Player 1 selects ability
2. Player 2 selects ability
3. Player 3 selects ability
4. Player 4 selects ability
5. Enemy turn (10 second delay)
   - Each alive enemy attacks
   - Randomly selects ability
   - Randomly selects target(s)
   - Applies damage with accuracy/evasion checks
   - Checks for player deaths
   - Regenerates battle screen if deaths occurred
   - Checks for battle end condition
6. Back to Player 1

**Dead players are automatically skipped in turn order**

**Battle End Conditions:**
- All players dead → Enemy wins
- Retreat button pressed → Battle ends

## Testing

All core calculations have been tested:
- ✓ Rarity multipliers
- ✓ EHP calculations
- ✓ Displayed HP calculations
- ✓ Damage application
- ✓ Accuracy/evasion rolls
- ✓ Character attribute loading
- ✓ Enemy attribute loading
- ✓ Boundary cases (overkill, zero damage, etc.)

## Future Implementation Notes

**Player Abilities:**
- Framework is in place for buffs/debuffs
- Currently player abilities only log actions
- When implementing, use the same attack resolution system as enemies
- Check `execute_enemy_turn()` for reference implementation

**Enemy Death (for player attacks):**
- Check enemy HP after player attacks
- If HP <= 0, mark as dead
- Call `regenerate_battle_screen()` to update image
- Check if all enemies dead → Player wins

**Buffs/Debuffs:**
- Add to `player_states[char]["buffs"]` or `["debuffs"]`
- Format: `{buff_name: {"value": float, "duration": int}}`
- Applied during stat calculations in combat
- Example: `{"atk_bonus": {"value": 0.15, "duration": 3}}`

## Code Structure

**New Helper Functions:**
- `parse_percentage_stat()`: Parse percentage stats safely
- `get_character_rarity_multiplier()`: Get R/SR/SSR multiplier
- `get_character_attributes()`: Load character base stats
- `calculate_ehp()`: Calculate total EHP
- `calculate_displayed_hp()`: Calculate displayed HP from EHP
- `apply_damage_to_ehp()`: Apply damage and return new EHP
- `roll_accuracy()`: Roll for accuracy
- `roll_evasion()`: Roll for evasion

**New BattleView Methods:**
- `get_alive_players()`: Get list of alive player characters
- `get_alive_enemies()`: Get list of alive enemies
- `create_hp_display()`: Generate HP status text
- `update_buff_debuff_durations()`: Manage buff/debuff timers
- `regenerate_battle_screen()`: Update battle image with current state

## Configuration

**Easy to Modify:**
- HP display format: Edit `create_hp_display()`
- Battle screen regeneration: Edit `regenerate_battle_screen()`
- Rarity multipliers: Edit `get_character_rarity_multiplier()`
- Enemy abilities: Edit `enemyAttributes` dictionary

## Security

✓ No security vulnerabilities detected by CodeQL scanner
✓ Safe percentage parsing with error handling
✓ Bounds checking on damage calculations
✓ Type checking on ability filtering
