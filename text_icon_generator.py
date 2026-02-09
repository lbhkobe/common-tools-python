#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Text Icon Generator
Generate .ico files with custom text and colors (128x128)
"""

import argparse
from PIL import Image, ImageDraw, ImageFont
import os


def generate_text_icon(text, output_path, text_color=(255, 255, 255), 
                      bg_color=None, size=128, font_size=None, bold=False, stroke_width=0):
    """
    Generate an ICO file with text
    
    Args:
        text: Text to display in the icon
        output_path: Path to save the .ico file
        text_color: RGB tuple for text color (default: white)
        bg_color: RGB tuple for background color (default: None - transparent)
        size: Icon size in pixels (default: 128)
        font_size: Font size (default: auto-calculated based on icon size)
        bold: Make text bold (default: False)
        stroke_width: Outline/stroke width to make text thicker (default: 0)
    
    Returns:
        Path to the generated icon file
    """
    # Create image with RGBA mode for transparency support
    if bg_color is None:
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))  # Transparent background
    else:
        img = Image.new('RGBA', (size, size), bg_color + (255,))
    draw = ImageDraw.Draw(img)
    
    # Calculate font size if not specified
    if font_size is None:
        font_size = int(size * 0.5)  # 50% of icon size
    
    # Try to load a font, fallback to default if not available
    try:
        # Try common Windows fonts (bold versions if requested)
        if bold:
            font_paths = [
                'C:/Windows/Fonts/arialbd.ttf',  # Arial Bold
                'C:/Windows/Fonts/calibrib.ttf',  # Calibri Bold
                'C:/Windows/Fonts/segoeuib.ttf',  # Segoe UI Bold
                '/System/Library/Fonts/Helvetica.ttc',  # macOS
                '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',  # Linux
            ]
        else:
            font_paths = [
                'C:/Windows/Fonts/arial.ttf',
                'C:/Windows/Fonts/calibri.ttf',
                'C:/Windows/Fonts/segoeui.ttf',
                '/System/Library/Fonts/Helvetica.ttc',  # macOS
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
            ]
        
        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
                break
        
        if font is None:
            # Use default font
            font = ImageFont.load_default()
            print("Warning: Using default font. Install TrueType fonts for better quality.")
    except Exception as e:
        print(f"Warning: Could not load TrueType font ({e}). Using default font.")
        font = ImageFont.load_default()
    
    # Get text bounding box for centering
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Calculate position to center text
    x = (size - text_width) / 2 - bbox[0]
    y = (size - text_height) / 2 - bbox[1]
    
    # Draw text with stroke/outline for extra thickness
    if stroke_width > 0:
        # Draw text with stroke (outline) to make it thicker
        draw.text((x, y), text, fill=text_color + (255,), font=font, 
                 stroke_width=stroke_width, stroke_fill=text_color + (255,))
    else:
        # Draw text without stroke
        draw.text((x, y), text, fill=text_color + (255,), font=font)
    
    # Ensure output path has .ico extension
    if not output_path.lower().endswith('.ico'):
        output_path += '.ico'
    
    # Save as ICO file - use only the main size to avoid Windows choosing smaller sizes
    img.save(output_path, format='ICO', sizes=[(size, size)])
    
    print(f"✓ Icon generated successfully: {output_path}")
    print(f"  Size: {size}x{size}")
    print(f"  Text: '{text}'")
    print(f"  Text color: RGB{text_color}")
    print(f"  Bold: {bold}")
    print(f"  Stroke width: {stroke_width}")
    if bg_color is None:
        print(f"  Background: Transparent")
    else:
        print(f"  Background color: RGB{bg_color}")
    
    return output_path


def parse_color(color_str):
    """
    Parse color string to RGB tuple
    
    Supported formats:
    - RGB: "255,255,255" or "255 255 255"
    - Hex: "#FFFFFF" or "FFFFFF"
    - Named colors: "white", "red", "blue", etc.
    
    Args:
        color_str: Color string
        
    Returns:
        RGB tuple (r, g, b)
    """
    color_str = color_str.strip()
    
    # Named colors
    named_colors = {
        'white': (255, 255, 255),
        'black': (0, 0, 0),
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0),
        'cyan': (0, 255, 255),
        'magenta': (255, 0, 255),
        'orange': (255, 165, 0),
        'purple': (128, 0, 128),
        'gray': (128, 128, 128),
        'grey': (128, 128, 128),
    }
    
    if color_str.lower() in named_colors:
        return named_colors[color_str.lower()]
    
    # Hex color
    if color_str.startswith('#'):
        color_str = color_str[1:]
    
    if len(color_str) == 6 and all(c in '0123456789ABCDEFabcdef' for c in color_str):
        r = int(color_str[0:2], 16)
        g = int(color_str[2:4], 16)
        b = int(color_str[4:6], 16)
        return (r, g, b)
    
    # RGB format
    if ',' in color_str or ' ' in color_str:
        parts = color_str.replace(',', ' ').split()
        if len(parts) == 3:
            try:
                r, g, b = [int(p) for p in parts]
                if all(0 <= c <= 255 for c in [r, g, b]):
                    return (r, g, b)
            except ValueError:
                pass
    
    raise ValueError(f"Invalid color format: {color_str}. Use RGB (255,255,255), Hex (#FFFFFF), or named color (white, red, etc.)")


def main():
    parser = argparse.ArgumentParser(
        description='Generate ICO files with custom text and colors (128x128)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate icon with text "A" and default colors
  python text_icon_generator.py "A" -o icon.ico
  
  # Custom text and background colors
  python text_icon_generator.py "APP" -o app.ico -tc white -bg blue
  
  # Using RGB values
  python text_icon_generator.py "X" -o x.ico -tc "255,0,0" -bg "0,0,0"
  
  # Using hex colors
  python text_icon_generator.py "!" -o alert.ico -tc "#FF0000" -bg "#FFFF00"
  
  # Custom size and font size
  python text_icon_generator.py "GO" -o go.ico -s 256 -fs 120
  
Supported color formats:
  - Named: white, black, red, green, blue, yellow, cyan, magenta, orange, purple, gray
  - RGB: "255,255,255" or "255 255 255"
  - Hex: "#FFFFFF" or "FFFFFF"
        """
    )
    
    parser.add_argument('text', help='Text to display in the icon')
    parser.add_argument('-o', '--output', required=True, help='Output .ico file path')
    parser.add_argument('-tc', '--text-color', default='white', 
                       help='Text color (default: white). Format: RGB, Hex, or named color')
    parser.add_argument('-bg', '--background-color', default=None,
                       help='Background color (default: transparent). Format: RGB, Hex, or named color')
    parser.add_argument('-s', '--size', type=int, default=128,
                       help='Icon size in pixels (default: 128)')
    parser.add_argument('-fs', '--font-size', type=int, default=None,
                       help='Font size (default: auto-calculated as 50%% of icon size)')
    parser.add_argument('-b', '--bold', action='store_true',
                       help='Make text bold (default: False)')
    parser.add_argument('-sw', '--stroke-width', type=int, default=0,
                       help='Stroke width to make text extra thick (0-20, default: 0). Try 5-10 for much bolder text')
    
    args = parser.parse_args()
    
    try:
        # Parse colors
        text_color = parse_color(args.text_color)
        bg_color = parse_color(args.background_color) if args.background_color else None
        
        # Generate icon
        generate_text_icon(
            text=args.text,
            output_path=args.output,
            text_color=text_color,
            bg_color=bg_color,
            size=args.size,
            font_size=args.font_size,
            bold=args.bold,
            stroke_width=args.stroke_width
        )
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
