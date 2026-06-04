# ============================================
# FILE: caption_generator.py
# PURPOSE: Gemini API से auto-caption + hashtags
# ============================================

import google.generativeai as genai
from .config import config
from .database import log_error
import re

# Gemini configure करो
genai.configure(api_key=config.GEMINI_API_KEY)
model = genai.GenerativeModel(config.GEMINI_MODEL)

# Rate limiting counter
rate_limit_counter = 0
MAX_RATE_LIMIT = config.GEMINI_RATE_LIMIT

def generate_caption_with_hashtags(news_title, ai_prompt=None):
    """
    Gemini API से caption + hashtags generate करो
    (Dynamic - हर बार नया unique caption)
    
    PARAMS:
        news_title: "Virat Kohli out"
        ai_prompt: Optional - background के लिए
    
    RETURN:
        dict: {
            'caption': 'Generated caption',
            'hashtags': '#trending #cricket #live'
        }
    """
    try:
        global rate_limit_counter
        
        # Rate limiting check करो
        rate_limit_counter += 1
        if rate_limit_counter > config.GEMINI_RATE_LIMIT:
            # Template fallback
            return get_template_caption(news_title)
        
        # Gemini prompt बनाओ
        prompt = f"""
        Cricket match का एक exciting commentary caption लिखो (Maximum 50 words, Hinglish mix):
        
        Event: {news_title}
        
        Rules:
        1. Hinglish mix करो (Hindi + English)
        2. Exciting aur energetic रखो
        3. Cricket terminology use करो
        4. Maximum 50 words
        5. कोई emoji use मत करो
        
        Caption लिख दो सीधे, कोई explanation नहीं:
        """
        
        # Gemini को call करो
        response = model.generate_content(prompt)
        caption = response.text.strip()
        
        # Caption clean करो (newlines remove)
        caption = caption.replace('\n', ' ')
        
        # Hashtags generate करो
        hashtags_prompt = f"""
        इस cricket caption के लिए relevant hashtags बना (5-7 hashtags):
        "{caption}"
        
        Rules:
        1. #trending ज़रूरी है
        2. #cricket ज़रूरी है
        3. Event-specific hashtags (जैसे #Kohli अगर Kohli का mention है)
        4. Sirf hashtags दो, कोई explanation नहीं
        
        Format: #hashtag1 #hashtag2 #hashtag3
        """
        
        hashtags_response = model.generate_content(hashtags_prompt)
        hashtags = hashtags_response.text.strip()
        
        log_error('success', f'Caption generated: {len(caption)} chars')
        
        return {
            'caption': caption,
            'hashtags': hashtags,
            'success': True
        }
        
    except Exception as e:
        log_error('gemini_error', 'Caption generation failed', str(e))
        
        # Template fallback करो
        return get_template_caption(news_title)

def get_template_caption(news_title):
    """
    Template-based caption (जब Gemini fail हो)
    
    TEMPLATES:
        Wicket: "Player out! What a moment!"
        Milestone: "Fantastic 50! Great batting!"
        Match: "Victory! Celebration time!"
    """
    try:
        templates = {
            'wicket': [
                f"Wicket! What a breakthrough moment! 🔥",
                f"Out! Excellent delivery! This is cricket!",
                f"Fantastic catch! Professional bowling!"
            ],
            'milestone': [
                f"50 runs! Great partnership building!",
                f"Century! Exceptional batting performance!",
                f"Brilliant knock! The batsman is in form!"
            ],
            'match_complete': [
                f"Victory! What a match! Celebration time!",
                f"Final result! Fantastic performance by the team!",
                f"Match over! Great cricket displayed!"
            ]
        }
        
        # Detect event type
        news_lower = news_title.lower()
        
        if 'out' in news_lower or 'wicket' in news_lower:
            template_type = 'wicket'
        elif '50' in news_lower or '100' in news_lower or 'century' in news_lower or 'fifty' in news_lower:
            template_type = 'milestone'
        elif 'win' in news_lower or 'won' in news_lower or 'victory' in news_lower:
            template_type = 'match_complete'
        else:
            template_type = 'milestone'
        
        import random
        caption = random.choice(templates.get(template_type, templates['milestone']))
        
        hashtags = "#trending #cricket #live #sports"
        
        log_error('success', 'Template caption used (Gemini fallback)')
        
        return {
            'caption': caption,
            'hashtags': hashtags,
            'success': True,
            'fallback': True
        }
        
    except Exception as e:
        log_error('api_error', 'Template caption failed', str(e))
        
        return {
            'caption': news_title,
            'hashtags': '#cricket #live',
            'success': True,
            'fallback': True
        }

def reset_rate_limit():
    """Rate limit counter को reset करो (हर घंटा)"""
    global rate_limit_counter
    rate_limit_counter = 0
    print("✅ Rate limit counter reset")
