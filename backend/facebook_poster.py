# ============================================
# FILE: facebook_poster.py
# PURPOSE: Facebook API integration - Auto-post
# ============================================

import requests
import os
from .config import config
from .database import log_error, fetch_one, execute_query

FACEBOOK_TOKEN = config.FACEBOOK_TOKEN
FACEBOOK_PAGE_ID = config.FACEBOOK_PAGE_ID
FACEBOOK_API_VERSION = config.FACEBOOK_API_VERSION

def post_to_facebook(post_id, image_path, caption):
    """
    Facebook page पर post करो
    
    PARAMS:
        post_id: Database post ID
        image_path: Local image file path
        caption: Post caption with hashtags
    
    RETURN:
        dict: {success: bool, facebook_post_id: str}
    """
    try:
        # अगर token placeholder है, तो skip करो
        if FACEBOOK_TOKEN == "your_facebook_token_here" or not FACEBOOK_TOKEN:
            log_error('info', 'Facebook token not set - skipping post')
            return {'success': False, 'message': 'Facebook token not configured'}
        
        # Image को read करो
        if not os.path.exists(image_path):
            log_error('file_error', f'Image not found: {image_path}')
            return {'success': False, 'message': 'Image file not found'}
        
        with open(image_path, 'rb') as f:
            files = {
                'source': f,
                'caption': (None, caption)
            }
            
            # Facebook Graph API endpoint
            url = f"https://graph.facebook.com/{FACEBOOK_API_VERSION}/{FACEBOOK_PAGE_ID}/photos"
            
            params = {
                'access_token': FACEBOOK_TOKEN
            }
            
            # POST करो
            response = requests.post(url, files=files, params=params, timeout=30)
            
            if response.status_code in [200, 201]:
                data = response.json()
                facebook_post_id = data.get('id')
                
                # Database update करो
                execute_query('''
                    UPDATE posts 
                    SET posted_to_facebook = 1, 
                        facebook_post_id = ?,
                        posted_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (facebook_post_id, post_id))
                
                log_error('success', f'Posted to Facebook: {facebook_post_id}')
                
                return {
                    'success': True,
                    'facebook_post_id': facebook_post_id,
                    'message': 'Posted successfully'
                }
            else:
                error_msg = response.text
                log_error('facebook_error', f'Post failed: {response.status_code}', error_msg)
                
                return {
                    'success': False,
                    'message': f'Facebook API error: {response.status_code}'
                }
        
    except requests.exceptions.RequestException as e:
        log_error('facebook_error', 'Post request failed', str(e))
        return {'success': False, 'message': 'Network error'}
    except Exception as e:
        log_error('api_error', 'Facebook posting failed', str(e))
        return {'success': False, 'message': str(e)}

def schedule_facebook_post(post_id):
    """
    Facebook queue में post को add करो (1-min gap)
    
    PARAMS:
        post_id: Database post ID
    
    RETURN:
        bool: Success या failure
    """
    try:
        # Post को queue में add करो
        execute_query('''
            INSERT INTO facebook_queue (post_id, status)
            VALUES (?, 'pending')
        ''', (post_id,))
        
        log_error('success', f'Post queued for Facebook: {post_id}')
        
        return True
        
    except Exception as e:
        log_error('api_error', 'Queue insertion failed', str(e))
        return False

def process_facebook_queue():
    """
    Facebook queue को process करो
    (1-min gap के साथ posts)
    
    यह function scheduler में हर minute call होगा
    """
    try:
        from datetime import datetime, timedelta
        
        # Pending posts लो (सबसे पुराना first)
        pending_posts = fetch_all('''
            SELECT fq.id, fq.post_id, p.image_path, p.caption, p.hashtags
            FROM facebook_queue fq
            JOIN posts p ON fq.post_id = p.id
            WHERE fq.status = 'pending'
            ORDER BY fq.queued_at ASC
            LIMIT 1
        ''')
        
        if not pending_posts:
            return False
        
        post = pending_posts[0]
        
        # Last posted time check करो (1-min gap)
        last_posted = fetch_one('''
            SELECT posted_at FROM posts 
            WHERE posted_to_facebook = 1 
            ORDER BY posted_at DESC 
            LIMIT 1
        ''')
        
        if last_posted and last_posted['posted_at']:
            last_time = datetime.fromisoformat(last_posted['posted_at'])
            current_time = datetime.now()
            time_diff = (current_time - last_time).total_seconds() / 60
            
            # अगर 1 minute से कम है, तो wait करो
            if time_diff < config.FACEBOOK_QUEUE_GAP_MINUTES:
                return False
        
        # Post करो
        full_caption = f"{post['caption']}\n{post['hashtags']}"
        
        result = post_to_facebook(post['post_id'], post['image_path'], full_caption)
        
        if result['success']:
            # Queue status update करो
            execute_query('''
                UPDATE facebook_queue 
                SET status = 'posted', posted_at = CURRENT_TIMESTAMP
                WHERE post_id = ?
            ''', (post['post_id'],))
            
            return True
        else:
            log_error('facebook_error', 'Failed to post to Facebook', result.get('message'))
            return False
        
    except Exception as e:
        log_error('api_error', 'Queue processing failed', str(e))
        return False

def check_facebook_connection():
    """
    Facebook token को validate करो
    
    RETURN:
        bool: Token valid या not
    """
    try:
        if FACEBOOK_TOKEN == "your_facebook_token_here" or not FACEBOOK_TOKEN:
            return False
        
        url = f"https://graph.facebook.com/{FACEBOOK_API_VERSION}/me"
        params = {'access_token': FACEBOOK_TOKEN}
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            log_error('success', 'Facebook connection valid')
            return True
        else:
            log_error('facebook_error', 'Facebook token invalid')
            return False
        
    except Exception as e:
        log_error('api_error', 'Facebook connection check failed', str(e))
        return False
