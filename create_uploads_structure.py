# ============================================
# File: create_uploads_structure.py
# Location: Project root में save करो
# (cricket-automation-system/ के अंदर)
# ============================================

import os

def create_uploads_structure():
    """Create uploads/ folder structure"""
    
    print("📍 Creating uploads/ structure...\n")
    
    # Main folders
    folders = [
        'uploads/players',
        'uploads/backgrounds',
        'uploads/sponsors',
        'uploads/generated/auto_posts',
        'uploads/generated/manual_posts',
        'uploads/generated/wicket_posts'
    ]
    
    # Create all folders
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"✅ {folder}")
    
    # Create .gitkeep files
    gitkeep_files = [
        'uploads/players/.gitkeep',
        'uploads/backgrounds/.gitkeep',
        'uploads/sponsors/.gitkeep'
    ]
    
    print("\nCreating .gitkeep files...")
    for file in gitkeep_files:
        with open(file, 'w') as f:
            pass  # Create empty file
        print(f"✅ {file}")
    
    print("\n" + "="*50)
    print("✅ UPLOADS STRUCTURE CREATED!")
    print("="*50 + "\n")
    
    # Verify
    print("📂 Folder structure:")
    for root, dirs, files in os.walk('uploads'):
        level = root.replace('uploads', '').count(os.sep)
        indent = ' ' * 2 * level
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            print(f'{subindent}{file}')

if __name__ == '__main__':
    create_uploads_structure()