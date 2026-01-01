# Battle System Mechanics

## Overview

The Battle System now includes interactive turn-based mechanics that allow players to control their team of characters against enemies.

## Features Implemented

### 1. Dynamic Ability Buttons
- Each character in your team has their own unique abilities
- R/SR characters have 3 abilities
- SSR characters have 4 abilities (including an Ultimate)
- Buttons automatically update when it's a new character's turn

### 2. Turn System
The battle follows a strict turn order:

1. **Character 1's Turn** - Player selects an ability
2. **Character 2's Turn** - Player selects an ability
3. **Character 3's Turn** - Player selects an ability
4. **Character 4's Turn** - Player selects an ability
5. **Enemy Turn** - 10 second delay, then enemy attacks (no implementation yet)
6. **Cycle repeats** - Back to Character 1

### 3. Retreat Button
- A red "Retreat" button is always available at the bottom of the battle screen
- Clicking it ends the battle immediately
- All buttons are disabled after retreating

## How to Use

1. Set up your team with `/team` command (up to 4 characters)
2. Start a battle with `/battle` command and choose an enemy
3. Click on ability buttons to use your character's skills
4. The turn automatically advances to the next character
5. After all 4 characters have acted, the enemy takes their turn
6. Click "Retreat" at any time to end the battle

## Character Abilities

### Example Characters:
- **r_abraize**: Punch, Sleep, Missing Assignments
- **ssr_abraize**: Accelerated Punch, Fast Forward, Rewind, Universal Stabilizer (Ultimate)
- **r_trey**: Punch, Irish Goodbye, Cheesy Fries
- **ssr_scottie**: Shield Bash, Guardian's Shield, Fortify, Eternal Watch (Ultimate)

*See the character info with `/char` command for full ability details*

## Technical Details

- Battle timeout: 5 minutes of inactivity
- Enemy turn delay: 10 seconds
- Only the battle initiator can use the buttons
- Abilities currently show a message but have no combat implementation (planned for future)

## Future Enhancements

The current implementation focuses on the turn system and UI mechanics. Future updates will include:
- Actual damage calculations
- HP tracking
- Status effects
- Battle outcomes (win/loss)
- Rewards system
