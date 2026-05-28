# ============================================
# File: download_fonts.py
# Location: Project ROOT (fonts/ के बाहर)
# ============================================

import os
import urllib.request

def download_fonts():
    """Download fonts from Google"""
    
    print("📍 Downloading fonts...\n")
    
    # Create fonts folder
    os.makedirs('static/fonts', exist_ok=True)
    
    # ============================================
    # FONT 1: Impact.ttf
    # ============================================
    
    print("1️⃣ Downloading Impact.ttf...")
    try:
        url = "https://github.com/google/fonts/raw/main/ofl/impact/Impact-Regular.ttf"
        path = 'static/fonts/Impact.ttf'
        urllib.request.urlretrieve(url, path)
        print(f"   ✅ Impact.ttf downloaded!\n")
    except:
        print("   ⚠️ Manual download: https://fonts.google.com/specimen/Impact\n")
    
    # ============================================
    # FONT 2: BebasNeue.ttf
    # ============================================
    
    print("2️⃣ Downloading BebasNeue.ttf...")
    try:
        url = "https://github.com/google/fonts/raw/main/ofl/bebasneue/BebasNeue-Regular.ttf"
        path = 'static/fonts/BebasNeue.ttf'
        urllib.request.urlretrieve(url, path)
        print(f"   ✅ BebasNeue.ttf downloaded!\n")
    except:
        print("   ⚠️ Manual download: https://fonts.google.com/specimen/Bebas+Neue\n")
    
    # ============================================
    # VERIFY
    # ============================================
    
    print("="*50)
    print("✅ FONTS READY!")
    print("="*50 + "\n")

if __name__ == '__main__':
    download_fonts()