# ============================================
# File: create_default_cricket.py
# Location: Project root में सेव करो
# ============================================

from PIL import Image, ImageDraw
import os

def create_default_cricket():
    """Default cricket player image बनाओ (400x400)"""
    
    print("📍 Creating default_cricket.png...\n")
    
    # Folder बनाओ अगर न हो
    os.makedirs('static/images', exist_ok=True)
    
    # Image बनाओ (transparent background)
    img = Image.new('RGBA', (400, 400), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Light blue background
    draw.rectangle([0, 0, 400, 400], fill=(200, 230, 255, 100))
    
    # Cricket field lines
    draw.line([200, 0, 200, 400], fill=(150, 150, 150, 150), width=2)
    draw.line([0, 200, 400, 200], fill=(150, 150, 150, 150), width=2)
    
    # Cricket stumps (background)
    for x in [150, 200, 250]:
        draw.rectangle([x-2, 100, x+2, 180], fill=(180, 120, 80, 200))
    
    # Player silhouette - head
    draw.ellipse([170, 80, 230, 140], fill=(100, 80, 60, 255))
    
    # Body
    draw.rectangle([175, 140, 225, 260], fill=(80, 80, 80, 255))
    
    # Arms
    draw.line([175, 160, 120, 180], fill=(100, 80, 60, 255), width=8)
    draw.line([225, 160, 280, 180], fill=(100, 80, 60, 255), width=8)
    
    # Bat (brown)
    draw.line([280, 180, 340, 100], fill=(120, 60, 20, 255), width=10)
    
    # Legs
    draw.line([190, 260, 180, 340], fill=(80, 80, 80, 255), width=6)
    draw.line([210, 260, 220, 340], fill=(80, 80, 80, 255), width=6)
    
    # Save करो
    path = 'static/images/default_cricket.png'
    img.save(path, 'PNG')
    
    print(f"✅ File created: {path}")
    print(f"✅ Size: 400x400 pixels")
    print(f"✅ Format: PNG (transparent background)")
    print(f"\n✅ default_cricket.png is ready!\n")

if __name__ == '__main__':
    create_default_cricket()