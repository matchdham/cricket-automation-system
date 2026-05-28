# ============================================
# FILE: auto_tracker.py
# PURPOSE: Auto-track ON/OFF toggle logic
# ============================================

from config import config
from database import log_error, execute_query, fetch_one
from scheduler import tracker
from cricket_api import get_current_matches
import threading
import time

class AutoTracker:
    """Auto-tracking को manage करो"""
    
    def __init__(self):
        self.is_enabled = config.AUTO_TRACK_DEFAULT
        self.is_running = False
        self.thread = None
    
    def enable_auto_tracking(self):
        """Auto-tracking शुरू करो"""
        try:
            if self.is_running:
                return {
                    'success': False,
                    'message': 'Already tracking'
                }
            
            self.is_enabled = True
            self.is_running = True
            
            # Scheduler के tracker को start करो
            tracker.start_tracking()
            
            log_error('success', 'Auto-tracking enabled')
            
            return {
                'success': True,
                'message': 'Auto-tracking enabled',
                'status': 'ON'
            }
        
        except Exception as e:
            log_error('api_error', 'Enable auto-tracking failed', str(e))
            return {
                'success': False,
                'message': str(e)
            }
    
    def disable_auto_tracking(self):
        """Auto-tracking बंद करो"""
        try:
            if not self.is_running:
                return {
                    'success': False,
                    'message': 'Already stopped'
                }
            
            self.is_enabled = False
            self.is_running = False
            
            # Scheduler के tracker को stop करो
            tracker.stop_tracking()
            
            log_error('success', 'Auto-tracking disabled')
            
            return {
                'success': True,
                'message': 'Auto-tracking disabled',
                'status': 'OFF'
            }
        
        except Exception as e:
            log_error('api_error', 'Disable auto-tracking failed', str(e))
            return {
                'success': False,
                'message': str(e)
            }
    
    def toggle_auto_tracking(self):
        """Auto-tracking toggle करो (ON ↔ OFF)"""
        try:
            if self.is_running:
                return self.disable_auto_tracking()
            else:
                return self.enable_auto_tracking()
        
        except Exception as e:
            log_error('api_error', 'Toggle auto-tracking failed', str(e))
            return {
                'success': False,
                'message': str(e)
            }
    
    def get_status(self):
        """Auto-tracking status get करो"""
        try:
            return {
                'success': True,
                'is_enabled': self.is_enabled,
                'is_running': self.is_running,
                'status': 'ON' if self.is_running else 'OFF'
            }
        
        except Exception as e:
            log_error('api_error', 'Get status failed', str(e))
            return {
                'success': False,
                'message': str(e)
            }
    
    def get_current_matches_count(self):
        """अभी कितने live matches हैं"""
        try:
            matches = get_current_matches()
            
            if not matches:
                return {
                    'success': True,
                    'count': 0,
                    'matches': []
                }
            
            matches_list = [
                {
                    'id': m.get('id'),
                    'name': m.get('name'),
                    'status': m.get('status')
                }
                for m in matches
            ]
            
            return {
                'success': True,
                'count': len(matches),
                'matches': matches_list
            }
        
        except Exception as e:
            log_error('api_error', 'Get matches count failed', str(e))
            return {
                'success': False,
                'count': 0,
                'message': str(e)
            }
    
    def start_tracking_specific_match(self, match_id):
        """Specific match को track करो"""
        try:
            tracker.tracked_matches[match_id] = None
            
            if not tracker.is_tracking:
                tracker.start_tracking(match_id)
            
            log_error('success', f'Tracking specific match: {match_id}')
            
            return {
                'success': True,
                'message': f'Tracking match: {match_id}'
            }
        
        except Exception as e:
            log_error('api_error', 'Start specific tracking failed', str(e))
            return {
                'success': False,
                'message': str(e)
            }
    
    def stop_tracking_specific_match(self, match_id):
        """Specific match को stop करो"""
        try:
            if match_id in tracker.tracked_matches:
                del tracker.tracked_matches[match_id]
            
            log_error('success', f'Stopped tracking: {match_id}')
            
            return {
                'success': True,
                'message': f'Stopped tracking: {match_id}'
            }
        
        except Exception as e:
            log_error('api_error', 'Stop specific tracking failed', str(e))
            return {
                'success': False,
                'message': str(e)
            }

# Global instance
auto_tracker = AutoTracker()

def enable_tracking():
    """Enable करो"""
    return auto_tracker.enable_auto_tracking()

def disable_tracking():
    """Disable करो"""
    return auto_tracker.disable_auto_tracking()

def toggle_tracking():
    """Toggle करो"""
    return auto_tracker.toggle_auto_tracking()

def get_tracking_status():
    """Status लो"""
    return auto_tracker.get_status()

def get_live_matches():
    """Live matches लो"""
    return auto_tracker.get_current_matches_count()

def track_match(match_id):
    """एक match track करो"""
    return auto_tracker.start_tracking_specific_match(match_id)

def untrack_match(match_id):
    """एक match untrack करो"""
    return auto_tracker.stop_tracking_specific_match(match_id)