# Battle System Documentation

## Overview
The battle system is a comprehensive turn-based combat system for the Discord bot where users can battle various enemies using their team of characters.

## How to Use
1. Set up a team using `/team` command (max 4 characters)
2. Start a battle using `/battle` command and select an enemy
3. During your turn, click ability buttons to use abilities
4. If multiple enemies exist, select which one to target
5. Battle continues until all enemies or all players are defeated

## Battle Flow

### 1. Initialization
- User starts battle with `/battle <enemy_type>`
- Battle state is created with player team and enemies
- Initial battle screen image is generated showing all characters
- First player's turn begins with ability buttons displayed

### 2. Player Turn
- Each player in the team gets a turn
- Player can select from 3 abilities (ultimates excluded for balance)
- If multiple enemies exist, player selects target
- Ability executes and battle log updates
- Dead characters are removed from battle screen
- Turn moves to next alive player

### 3. Enemy Turn
- After all players act, enemies take their turns
- Enemies use AI to select abilities and targets
- Jack Noir always targets the lowest HP player
- Each enemy action is logged
- 1 second delay between enemy actions
- Dead characters skipped automatically

### 4. Battle End
- Victory: All enemies defeated
- Defeat: All players defeated
- Final battle screen and log displayed

## Stats and Mechanics

### Base Stats
Each character has:
- **HP**: Health points
- **ATK**: Attack power
- **DEF**: Defense (reduces incoming damage)
- **EVA**: Evasion chance (0-100%)
- **ACC**: Accuracy (0-100%)

### Rarity Multipliers
Defense is multiplied by rarity for "effective HP":
- **R Rank**: 3x multiplier
- **SR Rank**: 5x multiplier  
- **SSR Rank**: 7x multiplier

### Damage Calculation
```
hit_chance = attacker_accuracy * (1 - defender_evasion)
if hit:
    effective_defense = defender_defense * rarity_multiplier
    damage = max(1, attacker_attack - effective_defense)
```

### Buffs and Debuffs
- Buffs/debuffs have a type (atk, def, eva, acc), value (percentage), and duration (turns)
- Applied before calculating effective stats
- Durations tick down at end of each round
- Stack additively (e.g., +10% atk + +20% atk = +30% atk)

### Special States
Various special states tracked per character:
- **Baller** (R Stephen): Stacks that provide ATK bonus
- **Accelerated** (SSR Abraize): Stacks that boost consecutive attacks
- **Considering** (SR Stephen): Stacks converted to damage
- **Bleed** (Jack Noir): Damage over time
- **Burn** (R Trey): Damage over time
- **Shield** (SSR Scottie): Absorbs damage
- **Stunned**: Character skips turn
- **Sleeping** (R Abraize): Cannot act, evasion 0%
- **Interfere** (R Noah): 50% chance to negate attack
- **Nervous** (SR Freeman): 25% chance to interrupt enemy attack

### Cooldowns
Abilities can have cooldowns preventing reuse:
- Tracked per ability index
- Shown on ability buttons
- Decremented at end of each round
- Cannot use ability while on cooldown

## Enemy Types

### Ruffian
- **HP**: 175
- **Stats**: Low attack/defense
- **Abilities**: Basic punch
- **Special**: 50% chance to spawn 1 or 2 Ruffians

### Grunt
- **HP**: 400
- **Stats**: High attack and defense
- **Abilities**: Punch, Slam (15 AOE damage)

### Spearman
- **HP**: 175
- **Stats**: Low attack/defense
- **Abilities**: Punch, Swipe (AOE), Stab (self-buff + damage)

### Agent
- **HP**: 175
- **Stats**: Low attack/defense
- **Abilities**: Punch, Sneak (+15% evasion)

### Jack Noir (Boss)
- **HP**: 1000
- **Stats**: High attack, moderate defense
- **Abilities**: Stab, Shiv (bleed), Slash (5 AOE + bleed)
- **Special**: Always targets lowest HP player

## Character Abilities

### R Characters
Basic abilities with simple mechanics:
- Basic attacks (Punch, Slap, Dropkick)
- Single buffs/debuffs
- Simple damage abilities

### SR Characters
Intermediate abilities with more complex mechanics:
- Multiple buffs/debuffs
- Conditional effects
- Longer durations

### SSR Characters  
Advanced abilities with powerful mechanics:
- Multiple stat buffs
- Special states
- Healing
- Ultimate abilities (4th slot, not used in normal turns)

## Implementation Details

### Files
- `main.py`: Core battle system, UI, and state management
- `battle_abilities.py`: All character and enemy ability implementations

### Key Classes
- **BattleState**: Manages entire battle state
- **BattleView**: Discord UI for ability selection
- **TargetSelectionView**: Discord UI for target selection

### Key Functions
- `execute_ability()`: Main ability execution dispatcher
- `execute_player_action()`: Handles player turn logic
- `enemy_turn()`: Handles enemy turn logic
- `create_battle_image()`: Generates dynamic battle screen
- `create_battle_embed()`: Creates Discord embed with battle info

## Edge Cases Handled
- Dead characters skip turns automatically
- Multiple enemies tracked with indices
- Dead characters removed from battle image
- Battle can't be started if already in battle
- Invalid targets handled gracefully
- All enemies/players dying mid-turn
- Cooldowns preventing ability spam
- Stats capped at reasonable values (e.g., evasion 0-100%)

## Future Enhancements
Potential additions:
- Experience/leveling system
- Rewards for winning battles
- More enemy types
- Team synergy bonuses
- Battle difficulty settings
- Replay/spectator mode
