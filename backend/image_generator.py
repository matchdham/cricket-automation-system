# ============================================
# FILE: image_generator.py
# PURPOSE: Pillow से image generation + Pollinations AI
# Mobile optimization (85% compress + lazy load)
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
        # Prompt को URL-safe बनाओ
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
            
    except requests.exceptions.Timeout:
        log_error('api_error', 'Pollinations API timeout')
        return None
    except Exception as e:
        log_error('api_error', 'Pollinations API error', str(e))
        return None

def create_default_background():
    """
    अगर Pollinations fail हो, तो default background बनाओ
    """
    try:
        img = Image.new('RGB', 
                       (config.IMAGE_WIDTH, config.IMAGE_HEIGHT), 
                       color=(25, 45, 90))
        return img
    except Exception as e:
        log_error('api_error', 'Default background error', str(e))
        return None

def detect_text_color(image):
    """
    Background image का average color detect करके अच्छा text color decide करो
    """
    try:
        small_img = image.resize((100, 100))
        pixels = list(small_img.getdata())
        avg_r = sum(p[0] for p in pixels) // len(pixels)
        avg_g = sum(p[1] for p in pixels) // len(pixels)
        avg_b = sum(p[2] for p in pixels) // len(pixels)
        
        brightness = (avg_r + avg_g + avg_b) / 3
        
        if brightness < 128:
            return (255, 255, 255)  # White
        else:
            return (0, 0, 0)  # Black
            
    except Exception as e:
        log_error('api_error', 'Text color detection error', str(e))
        return (255, 255, 255)  # Default white

def load_font(font_name='Impact.ttf', size=100):
    """
    Font load करो (static/fonts/ से)
    """
    try:
        font_path = os.path.join(config.FONTS_FOLDER, font_name)
        
        if not os.path.exists(font_path):
            log_error('file_error', f'Font not found: {font_name}')
            return ImageFont.load_default()
        
        font = ImageFont.truetype(font_path, size=size)
        return font
    except Exception as e:
        log_error('font_error', f'Font load failed: {font_name}', str(e))
        return ImageFont.load_default()

def wrap_text(text, max_width, font, draw):
    """
    लंबे text को wrap करो (multiple lines)
    """
    try:
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            
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
        log_error('text_error', 'Text wrap error', str(e))
        return [text]

def create_graphic_with_text(news_title, background_image=None, text_bold=False, 
                            sponsor_logo=None, ai_prompt=None):
    """
    Final graphic बनाओ और उसे uploads/generated/ folder में सुरक्षित save करो
    """
    try:
        # Canvas बनाओ (Default Background)
        canvas = Image.new('RGB', 
                          (config.IMAGE_WIDTH, config.IMAGE_HEIGHT),
                          color=(25, 45, 90))
        
        # 1. Custom Background Layer Check
        if background_image and os.path.exists(background_image):
            try:
                bg_img = Image.open(background_image)
                bg_img = bg_img.resize((config.IMAGE_WIDTH, config.IMAGE_HEIGHT))
                canvas = bg_img
            except Exception as e:
                log_error('image_error', 'Background image load failed', str(e))
        
        # 2. AI Prompt Background Layer Check (अगर Custom BG नहीं है)
        elif ai_prompt:
            bg_img = get_background_from_pollinations(ai_prompt)
            if bg_img:
                bg_img = bg_img.resize((config.IMAGE_WIDTH, config.IMAGE_HEIGHT))
                canvas = bg_img
        
        draw = ImageDraw.Draw(canvas)
        text_color = detect_text_color(canvas)
        
        # Font choose करो
        if text_bold:
            font = load_font('Impact.ttf', size=100)
        else:
            font = load_font('RobotoBold.ttf', size=80)
        
        # Text alignment aur wrapping setup
        lines = wrap_text(news_title, config.IMAGE_WIDTH - 60, font, draw)
        total_height = len(lines) * 120
        start_y = (config.IMAGE_HEIGHT - total_height) // 2
        
        # Text draw karo shadow effect ke sath
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = (config.IMAGE_WIDTH - text_width) // 2
            text_y = start_y + (i * 120)
            
            draw.text((text_x + 2, text_y + 2), line, fill=(0, 0, 0), font=font)
            draw.text((text_x, text_y), line, fill=text_color, font=font)
        
        # 3. Sponsor Logo Watermark Layer
        if sponsor_logo and os.path.exists(sponsor_logo):
            try:
                sponsor = Image.open(sponsor_logo)
                sponsor = sponsor.resize((config.SPONSOR_SIZE[0], config.SPONSOR_SIZE[1]))
                
                sponsor_x = config.IMAGE_WIDTH - config.SPONSOR_SIZE[0] - config.SPONSOR_MARGIN
                sponsor_y = config.IMAGE_HEIGHT - config.SPONSOR_SIZE[1] - config.SPONSOR_MARGIN
                
                canvas.paste(sponsor, (sponsor_x, sponsor_y))
            except Exception as e:
                log_error('image_error', 'Sponsor watermark failed', str(e))
        
        # Mobile optimization compress handler
        if config.IMAGE_OPTIMIZATION_ENABLED:
            canvas = canvas.resize((config.IMAGE_WIDTH, config.IMAGE_HEIGHT), 
                                  Image.Resampling.LANCZOS)
        
        # ============================================
        # RAILWAY FIX: CRASH SE BACHNE KE LIYE FIXED FOLDER
        # ============================================
        output_folder = os.path.join('uploads', 'generated')
        if not os.path.exists(output_folder):
            os.makedirs(output_folder, exist_ok=True)
        
        timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"post_{timestamp}.png"
        output_path = os.path.join(output_folder, filename)
        
        # Save post graphic asset
        canvas.save(output_path, 'PNG', quality=config.IMAGE_QUALITY)
        
        log_error('success', f'Image created successfully: {filename}')
        return output_path
        
    except Exception as e:
        log_error('image_error', 'Failed to create graphic inside generator', str(e))
        return None

def optimize_image_for_mobile(image_path):
    """
    Image को mobile के लिए optimize करो
    """
    try:
        img = Image.open(image_path)
        optimized_path = image_path.replace('.png', '_optimized.png')
        img.save(optimized_path, 'PNG', quality=85)
        
        os.remove(image_path)
        os.rename(optimized_path, image_path)
        
        log_error('success', f'Image optimized: {image_path}')
        return True
    except Exception as e:
        log_error('image_error', 'Image optimization failed', str(e))
        return False
        
        
