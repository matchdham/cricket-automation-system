# ============================================
# FILE: scheduler.py
# PURPOSE: 4-min scheduler - Parallel tracking
# ============================================

import threading
import time
from datetime import datetime
from config import config
from database import log_error, fetch_one, execute_query
from cricket_api import get_current_matches, get_match_info, detect_wickets, detect_milestone
from caption_generator import generate_caption_with_hashtags
from image_generator import create_graphic_with_text
from facebook_poster import schedule_facebook_post

class MatchTracker:
    """
    Live match को track करो
    Wickets, milestones, और events detect करो
    """
    
    def __init__(self):
        self.is_tracking = False
        self.thread = None
        self.tracked_matches = {}
        self.auto_track_enabled = config.AUTO_TRACK_DEFAULT
    
    def start_tracking(self, match_id=None):
        """
        Tracking शुरू करो
        
        PARAMS:
            match_id: Specific match या None (auto-track all)
        """
        try:
            if self.is_tracking:
                print("⚠️ Already tracking")
                return
            
            self.is_tracking = True
            self.auto_track_enabled = True
            
            if match_id:
                self.tracked_matches[match_id] = None
            
            # Background thread start करो
            self.thread = threading.Thread(target=self._tracking_loop, daemon=True)
            self.thread.start()
            
            log_error('success', 'Tracking started')
            print("✅ Tracking started")
            
        except Exception as e:
            log_error('api_error', 'Tracking start failed', str(e))
    
    def stop_tracking(self):
        """Tracking बंद करो"""
        try:
            self.is_tracking = False
            self.auto_track_enabled = False
            self.tracked_matches = {}
            
            log_error('success', 'Tracking stopped')
            print("✅ Tracking stopped")
            
        except Exception as e:
            log_error('api_error', 'Tracking stop failed', str(e))
    
    def toggle_auto_track(self, enabled):
        """Auto-track toggle करो"""
        self.auto_track_enabled = enabled
        status = "ON" if enabled else "OFF"
        print(f"✅ Auto-track: {status}")
    
    def _tracking_loop(self):
        """
        4-minute interval में scores check करो
        (Parallel tracking - सभी matches)
        """
        try:
            while self.is_tracking:
                # 4 minutes wait करो
                time.sleep(config.SCORE_UPDATE_INTERVAL)
                
                if not self.is_tracking:
                    break
                
                print(f"\n📊 Score update at {datetime.now().strftime('%H:%M:%S')}")
                
                # Current matches fetch करो
                matches = get_current_matches()
                
                if not matches:
                    print("❌ No matches found")
                    continue
                
                # सभी matches को parallel process करो
                for match in matches:
                    try:
                        match_id = match.get('id')
                        match_name = match.get('name', 'Unknown')
                        
                        # Auto-track check करो
                        if self.auto_track_enabled or match_id in self.tracked_matches:
                            self._process_match(match_id, match_name)
                    
                    except Exception as e:
                        log_error('api_error', f'Match processing failed: {match_id}', str(e))
                
                print("✅ Score update complete")
        
        except Exception as e:
            log_error('api_error', 'Tracking loop error', str(e))
    
    def _process_match(self, match_id, match_name):
        """
        एक match को process करो
        (Wickets, milestones, events detect करो)
        """
        try:
            # Match info fetch करो
            current_data = get_match_info(match_id)
            
            if not current_data:
                return
            
            # Previous state लो
            previous_data = self.tracked_matches.get(match_id)
            
            # Wickets detect करो
            if previous_data:
                new_wickets = detect_wickets(previous_data, current_data)
                
                for wicket in new_wickets:
                    self._create_wicket_post(match_name, wicket)
            
            # Milestone detect करो
            current_score = current_data.get('score', {}).get('team_a', {}).get('r', 0)
            previous_score = previous_data.get('score', {}).get('team_a', {}).get('r', 0) if previous_data else 0
            
            milestones = detect_milestone(previous_score, current_score)
            
            for milestone in milestones:
                self._create_milestone_post(match_name, milestone)
            
            # Current state save करो (next comparison के लिए)
            self.tracked_matches[match_id] = current_data
            
            print(f"✅ Processed: {match_name}")
        
        except Exception as e:
            log_error('api_error', f'Match processing error: {match_id}', str(e))
    
    def _create_wicket_post(self, match_name, wicket):
        """Wicket का post create करो"""
        try:
            player = wicket.get('player', 'Player')
            wicket_info = wicket.get('wicket_info', 'Out')
            
            news_title = f"{player} {wicket_info} - {match_name}"
            
            # Caption generate करो
            caption_data = generate_caption_with_hashtags(news_title)
            caption = caption_data.get('caption', news_title)
            hashtags = caption_data.get('hashtags', '#cricket #live')
            
            # Image create करो
            final_caption = f"{caption}\n{hashtags}"
            
            image_path = create_graphic_with_text(
                news_title=final_caption,
                ai_prompt="Cricket wicket moment",
                text_bold=True
            )
            
            if image_path:
                # Database में save करो
                execute_query('''
                    INSERT INTO posts 
                    (news_title, image_path, caption, hashtags, background_type, created_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (news_title, image_path, caption, hashtags, 'auto', 1))
                
                # Facebook queue में add करो
                post = fetch_one('SELECT id FROM posts ORDER BY id DESC LIMIT 1')
                if post:
                    schedule_facebook_post(post['id'])
                
                log_error('success', f'Wicket post created: {player}')
                print(f"🎯 Wicket post: {player}")
        
        except Exception as e:
            log_error('api_error', 'Wicket post creation failed', str(e))
    
    def _create_milestone_post(self, match_name, milestone):
        """Milestone का post create करो"""
        try:
            news_title = f"{milestone} runs milestone! - {match_name}"
            
            # Caption generate करो
            caption_data = generate_caption_with_hashtags(news_title)
            caption = caption_data.get('caption', news_title)
            hashtags = caption_data.get('hashtags', '#cricket #live')
            
            # Image create करो
            final_caption = f"{caption}\n{hashtags}"
            
            image_path = create_graphic_with_text(
                news_title=final_caption,
                ai_prompt="Cricket milestone celebration"
            )
            
            if image_path:
                # Database में save करो
                execute_query('''
                    INSERT INTO posts 
                    (news_title, image_path, caption, hashtags, background_type, created_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (news_title, image_path, caption, hashtags, 'auto', 1))
                
                # Facebook queue में add करो
                post = fetch_one('SELECT id FROM posts ORDER BY id DESC LIMIT 1')
                if post:
                    schedule_facebook_post(post['id'])
                
                log_error('success', f'Milestone post created: {milestone}')
                print(f"🎯 Milestone post: {milestone}")
        
        except Exception as e:
            log_error('api_error', 'Milestone post creation failed', str(e))

# Global tracker instance
tracker = MatchTracker()

def start_auto_tracking():
    """Auto-tracking शुरू करो (सभी matches)"""
    tracker.start_tracking()

def stop_auto_tracking():
    """Auto-tracking बंद करो"""
    tracker.stop_tracking()

def track_specific_match(match_id):
    """Specific match को track करो"""
    tracker.tracked_matches[match_id] = None
    if not tracker.is_tracking:
        tracker.start_tracking(match_id)

def toggle_auto_track(enabled):
    """Auto-track toggle करो"""
    tracker.toggle_auto_track(enabled)