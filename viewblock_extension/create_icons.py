#!/usr/bin/env python3
"""
Create placeholder icons for the ViewBlock Chrome extension
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    """Create a simple icon with the specified size"""
    # Create a new image with a white background
    img = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple border
    border_width = max(1, size // 32)
    draw.rectangle([border_width, border_width, size-border_width, size-border_width], 
                   outline='#4CAF50', width=border_width)
    
    # Draw a simple "V" for ViewBlock
    font_size = size // 3
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    text = "V"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    draw.text((x, y), text, fill='#4CAF50', font=font)
    
    # Save the image
    img.save(filename)
    print(f"Created {filename} ({size}x{size})")

def main():
    """Create all required icons"""
    icons = [
        (16, "icon16.png"),
        (48, "icon48.png"),
        (128, "icon128.png")
    ]
    
    for size, filename in icons:
        create_icon(size, filename)
    
    print("All icons created successfully!")

if __name__ == "__main__":
    main() 