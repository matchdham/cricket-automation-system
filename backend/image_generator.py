# ============================================
# FILE: image_generator.py
# PURPOSE: Pillow से image generation + Pollinations AI
# Root path auto-folder creator included
# ============================================

from PIL import Image, ImageDraw, ImageFont
import requests
import os
from .config import config
from .database import log_error
import io

def get_background_from_pollinations(prompt):
    """
    Pollinations AI से direct image fetch करो (No API key needed)
    """
    try:
        safe_prompt = prompt.replace(" ", "%20")
        url = f"https://image.pollinations.ai/p/{safe_prompt}?width=1080&height=1080&model=flux&nologo=true"
        
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            img = Image.open(io.BytesIO(response.content))
            if img.mode != 'RGB':
                img = img.convert('RGB')
            log_error('success', 'Background fetched from Pollinations AI')
            return img
        else:
            log_error('api_error', f'Pollinations API failed: {response.status_code}')
            return None
    except Exception as e:
        log_error('api_error', 'Pollinations API error', str(e))
        return None

def create_default_background():
    """
    अगर Pollinations fail हो, तो default background बनाओ
    """
    try:
        return Image.new('RGB', (config.IMAGE_WIDTH, config.IMAGE_HEIGHT), color=(25, 45, 90))
    except Exception as e:
        log_error('api_error', 'Default background error', str(e))
        return None

def detect_text_color(image):
    """
    Background image का average color detect करके text color manage करो
    """
    try:
        small_img = image.resize((100, 100))
        pixels = list(small_img.getdata())
        avg_r = sum(p[0] for p in pixels) // len(pixels)
        avg_g = sum(p[1] for p in pixels) // len(pixels)
        avg_b = sum(p[2] for p in pixels) // len(pixels)
        
        brightness = (avg_r + avg_g + avg_b) / 3
        return (255, 255, 255) if brightness < 128 else (0, 0, 0)
    except Exception as e:
        return (255, 255, 255)

def load_font(font_name='Impact.ttf', size=100):
    """
    Font load करो (Case-sensitivity aur paths bypass handler)
    """
    try:
        font_folder = getattr(config, 'FONTS_FOLDER', os.path.join('static', 'fonts'))
        
        # GitHub casing mismatch fix (Impact.ttf vs impact.ttf)
        if font_name == 'Impact.ttf':
            primary_path = os.path.join(font_folder, 'Impact.ttf')
            secondary_path = os.path.join(font_folder, 'impact.ttf')
            font_path = primary_path if os.path.exists(primary_path) else secondary_path
        else:
            font_path = os.path.join(font_folder, font_name)
        
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size=size)
            
        # Linux Server Standard Fallbacks
        system_fonts = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
        ]
        for sys_font in system_fonts:
            if os.path.exists(sys_font):
                return ImageFont.truetype(sys_font, size=size)
                
        return ImageFont.load_default()
    except Exception as e:
        log_error('font_error', f'Font load failed: {font_name}', str(e))
        return ImageFont.load_default()

def wrap_text(text, max_width, font, draw):
    """
    लंबे text को safe wrap करो lines में
    """
    try:
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            try:
                bbox = draw.textbbox((0, 0), test_line, font=font)
                width = bbox[2] - bbox[0]
            except AttributeError:
                width = 400
                
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        return lines
    except Exception as e:
        return [text]

def create_graphic_with_text(news_title, background_image=None, text_bold=False, 
                            sponsor_logo=None, ai_prompt=None):
    """
    Final graphic बनाओ और उसे main project root directory के uploads/generated में save करो
    """
    try:
        # Default Base Canvas
        canvas = Image.new('RGB', (config.IMAGE_WIDTH, config.IMAGE_HEIGHT), color=(25, 45, 90))
        
        # 1. Background Setup
        if background_image and os.path.exists(background_image):
            try:
                bg_img = Image.open(background_image)
                canvas = bg_img.resize((config.IMAGE_WIDTH, config.IMAGE_HEIGHT))
            except Exception as e:
                log_error('image_error', 'Custom background load failed', str(e))
        elif ai_prompt:
            bg_img = get_background_from_pollinations(ai_prompt)
            if bg_img:
                canvas = bg_img.resize((config.IMAGE_WIDTH, config.IMAGE_HEIGHT))
        
        draw = ImageDraw.Draw(canvas)
        text_color = detect_text_color(canvas)
        
        # 2. Font Loading
        font = load_font('Impact.ttf', size=100) if text_bold else load_font('BebasNeue.ttf', size=90)
        
        # 3. Text Wrapping and Processing
        lines = wrap_text(news_title, config.IMAGE_WIDTH - 60, font, draw)
        total_height = len(lines) * 120
        start_y = (config.IMAGE_HEIGHT - total_height) // 2
        
        # Text Drawing loop
        for i, line in enumerate(lines):
            try:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
            except AttributeError:
                text_width = 400
                
            text_x = (config.IMAGE_WIDTH - text_width) // 2
            text_y = start_y + (i * 120)
            
            # Text shadow and overlay text layers
            draw.text((text_x + 3, text_y + 3), line, fill=(0, 0, 0), font=font)
            draw.text((text_x, text_y), line, fill=text_color, font=font)
        
        # 4. Sponsor Logo Insertion
        if sponsor_logo and os.path.exists(sponsor_logo):
            try:
                sponsor = Image.open(sponsor_logo)
                sponsor = sponsor.resize((config.SPONSOR_SIZE[0], config.SPONSOR_SIZE[1]))
                sponsor_x = config.IMAGE_WIDTH - config.SPONSOR_SIZE[0] - config.SPONSOR_MARGIN
                sponsor_y = config.IMAGE_HEIGHT - config.SPONSOR_SIZE[1] - config.SPONSOR_MARGIN
                canvas.paste(sponsor, (sponsor_x, sponsor_y))
            except Exception as e:
                log_error('image_error', 'Sponsor watermark crash', str(e))
        
        # Mobile optimization compress
        if config.IMAGE_OPTIMIZATION_ENABLED:
            canvas = canvas.resize((config.IMAGE_WIDTH, config.IMAGE_HEIGHT), Image.Resampling.LANCZOS)
        
        # ============================================
        # RAILWAY ABSOLUTE ROOT PATH GENERATION
        # ============================================
        current_dir = os.path.dirname(os.path.abspath(__file__)) # 'backend' folder
        root_dir = os.path.dirname(current_dir) # main project root folder
        output_folder = os.path.join(root_dir, 'uploads', 'generated')
        
        # Automate directory creation check
        if not os.path.exists(output_folder):
            os.makedirs(output_folder, exist_ok=True)
            
        timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"post_{timestamp}.png"
        output_path = os.path.join(output_folder, filename)
        
        # Final image asset save rule
        canvas.save(output_path, 'PNG', quality=config.IMAGE_QUALITY)
        
        log_error('success', f'Image successfully generated at: {output_path}')
        
        # Return exact string required by serving route
        return os.path.join('uploads', 'generated', filename)
        
    except Exception as e:
        log_error('image_error', 'Failed inside create_graphic_with_text', str(e))
        return None

def optimize_image_for_mobile(image_path):
    try:
        img = Image.open(image_path)
        optimized_path = image_path.replace('.png', '_optimized.png')
        img.save(optimized_path, 'PNG', quality=85)
        os.remove(image_path)
        os.rename(optimized_path, image_path)
        return True
    except Exception as e:
        return False
                
        
        
