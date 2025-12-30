#!/usr/bin/env python3
"""
Helper script to calculate character feet positions for new characters.

This script analyzes character PNG files and outputs the default feet positions
that can be used in the characterFeet dictionary.

Usage:
    python calculate_feet.py <character_image.png>
    python calculate_feet.py --all  (to process all character images)
"""

import sys
import os
from PIL import Image

def calculate_feet_position(image_path):
    """
    Calculate the default feet position for a character image.
    
    Args:
        image_path: Path to the character PNG file
        
    Returns:
        Tuple of (x, y) representing the feet position
    """
    if not os.path.exists(image_path):
        print(f"Error: File not found: {image_path}")
        return None
    
    try:
        img = Image.open(image_path)
        width, height = img.size
        
        # Default feet position is at bottom-middle
        feet_x = width // 2
        feet_y = height
        
        return (feet_x, feet_y, width, height)
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    if sys.argv[1] == "--all":
        # Process all character images in the current directory
        character_files = [
            "r_abraize.png", "r_abraize2.png", "sr_abraize.png", "ssr_abraize.png",
            "r_trey.png", "sr_trey.png", "ssr_trey.png",
            "r_noah.png",
            "r_freeman.png", "sr_freeman.png",
            "ssr_jayden.png",
            "r_stephen.png", "sr_stephen.png",
            "sr_homestuck.png",
            "ssr_scottie.png"
        ]
        
        print("Character Feet Positions")
        print("=" * 70)
        print("Copy these values into the characterFeet dictionary in main.py")
        print("=" * 70)
        print()
        print("characterFeet = {")
        
        for char_file in sorted(character_files):
            if os.path.exists(char_file):
                result = calculate_feet_position(char_file)
                if result:
                    feet_x, feet_y, width, height = result
                    char_name = char_file.replace(".png", "")
                    print(f'    "{char_name}": ({feet_x}, {feet_y}),  # Image size: {width}x{height}')
            else:
                char_name = char_file.replace(".png", "")
                print(f'    # "{char_name}": (?, ?),  # FILE NOT FOUND')
        
        print("}")
    else:
        # Process single file
        image_path = sys.argv[1]
        result = calculate_feet_position(image_path)
        
        if result:
            feet_x, feet_y, width, height = result
            char_name = os.path.basename(image_path).replace(".png", "")
            
            print(f"Character: {char_name}")
            print(f"Image size: {width}x{height}")
            print(f"Feet position: ({feet_x}, {feet_y})")
            print()
            print("Add this to characterFeet dictionary:")
            print(f'    "{char_name}": ({feet_x}, {feet_y}),')

if __name__ == "__main__":
    main()
