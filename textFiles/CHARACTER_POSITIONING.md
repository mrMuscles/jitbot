# Dynamic Character Positioning System

## Overview

The battle screen now uses a dynamic positioning system that places characters based on their "feet" position. This prevents characters from floating, being cut off at the edges, or overlapping incorrectly.

## How It Works

The system works in 3 steps:

1. **Character Feet Positions**: Each character has a defined "feet" position within their sprite (stored in `characterFeet` dictionary)
2. **Team Slot Ground Positions**: The battle screen has 4 ground positions where character feet should touch (stored in `teamSlotGroundPositions`)
3. **Dynamic Calculation**: The system calculates where to paste each character image so their feet align with the ground position

### Boundary Protection

The system automatically prevents characters from being cut off by:
- Checking if the character would extend beyond the right edge
- Checking if the character would extend beyond the bottom edge
- Checking if the character would extend beyond the left edge
- Checking if the character would extend beyond the top edge
- Adjusting the paste position if any cutoff would occur

### Floating Characters

Some characters (like `ssr_scottie`) are designed to float above the ground. These characters have special Y-axis offsets defined in the `characterFloatingOffset` dictionary.

### Character Layering

Characters are pasted on the battle screen in reverse order (from slot 4 to slot 1), ensuring that:
- **Slot 1** (index 0) appears on top (pasted last)
- **Slot 2** (index 1) appears below slot 1
- **Slot 3** (index 2) appears below slot 2
- **Slot 4** (index 3) appears at the back (pasted first)

This creates a natural visual depth where front characters overlap those behind them.

## Adding a New Character

To add a new character to the system:

1. **Add the character PNG file** to the repository
2. **Add to characterImages dictionary** (if not already present)
3. **Calculate feet position** using one of these methods:

   **Option A: Use the helper script**
   ```bash
   python3 calculate_feet.py character_name.png
   ```
   
   **Option B: Manual calculation**
   - Open the image and get its dimensions (width, height)
   - Default feet position is `(width/2, height)` - bottom-middle
   - If the character's feet are off-center, adjust the X coordinate accordingly
   
4. **Add entry to characterFeet dictionary**:
   ```python
   characterFeet = {
       # ... existing entries ...
       "new_character": (feet_x, feet_y),
   }
   ```

5. **(Optional) Add floating offset** if the character should float:
   ```python
   characterFloatingOffset = {
       # ... existing entries ...
       "new_character": -20,  # Negative moves up, positive moves down
   }
   ```

## Fine-Tuning Character Positions

If a character doesn't look right in the battle screen:

1. **Test the current positioning**:
   - Run the battle command with a team containing the character
   - Examine the output battle_screen.png

2. **Adjust the feet position**:
   - If feet are too far left/right: adjust the X coordinate in `characterFeet`
   - If the character is too high/low: adjust the Y coordinate in `characterFeet`

3. **Adjust floating offset** (if needed):
   - Add or modify entry in `characterFloatingOffset`
   - Use negative values to move character up (floating)
   - Use positive values to move character down (sinking)

## Example

For a character image that is 100x200 pixels:

```python
# Default feet position (bottom-middle)
"example_char": (50, 200),

# If feet are 10 pixels from the left edge
"example_char": (10, 200),

# If character should float 15 pixels up
characterFloatingOffset = {
    "example_char": -15,
}
```

## Batch Processing

To recalculate all character feet positions at once:

```bash
cd /home/runner/work/jitbot/jitbot
python3 calculate_feet.py --all
```

This will output the feet positions for all character PNG files in the directory, which you can copy into the `characterFeet` dictionary.

## Configuration Variables

### characterFeet
Dictionary mapping character names to their feet positions within the sprite.
- Format: `{"char_name": (x, y)}`
- `x`: Horizontal offset from left edge to feet center
- `y`: Vertical offset from top edge to feet bottom

### characterFloatingOffset
Dictionary mapping character names to vertical offsets for floating/sinking effects.
- Format: `{"char_name": offset}`
- Negative offset: character moves UP (floating)
- Positive offset: character moves DOWN (sinking)

### teamSlotGroundPositions
List of 4 ground positions on the battle screen where character feet should touch.
- Format: `[(x1, y1), (x2, y2), (x3, y3), (x4, y4)]`
- Slot 0: Front-right position
- Slot 1: Middle-right position
- Slot 2: Back-right position
- Slot 3: Far-back position

## Background Information

- Background image size: 651x419 pixels
- Coordinate system: (0, 0) is top-left, (651, 419) is bottom-right
- Characters are placed on top of enemies in the layering order
