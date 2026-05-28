# ============================================
# FILE: event_detector.py
# PURPOSE: Wicket/Century/Milestone detection
# ============================================

from config import config
from database import log_error, fetch_one, execute_query
from cricket_api import get_match_info

class EventDetector:
    """Live match events को detect करो"""
    
    def __init__(self):
        self.previous_match_state = {}
    
    def detect_events(self, match_id, current_match_data):
        """
        Match में सभी events detect करो
        
        RETURNS:
            list: [event1, event2, ...]
        """
        try:
            events = []
            
            # Previous state लो
            previous_state = self.previous_match_state.get(match_id)
            
            if not previous_state:
                self.previous_match_state[match_id] = current_match_data
                return events
            
            # Wickets detect करो
            wickets = self.detect_wickets(previous_state, current_match_data)
            if wickets:
                events.extend(wickets)
            
            # Milestones detect करो
            milestones = self.detect_milestones(previous_state, current_match_data)
            if milestones:
                events.extend(milestones)
            
            # Century detect करो
            centuries = self.detect_centuries(previous_state, current_match_data)
            if centuries:
                events.extend(centuries)
            
            # Match complete detect करो
            match_complete = self.detect_match_complete(current_match_data)
            if match_complete:
                events.extend(match_complete)
            
            # Current state save करो
            self.previous_match_state[match_id] = current_match_data
            
            return events
        
        except Exception as e:
            log_error('api_error', 'Event detection failed', str(e))
            return []
    
    def detect_wickets(self, previous_state, current_state):
        """Wickets detect करो"""
        try:
            wickets = []
            
            prev_scorecard = previous_state.get('scorecard', {})
            curr_scorecard = current_state.get('scorecard', {})
            
            # Team A में चेक करो
            for curr_player in curr_scorecard.get('team_a', []):
                player_name = curr_player.get('name')
                curr_status = curr_player.get('wicket', 'not out')
                
                # पिछली state में खोजो
                prev_player = next((p for p in prev_scorecard.get('team_a', []) 
                                   if p.get('name') == player_name), None)
                prev_status = prev_player.get('wicket', 'not out') if prev_player else 'not out'
                
                # अगर पहले "not out" था और अब out है
                if prev_status == 'not out' and curr_status != 'not out':
                    wickets.append({
                        'type': 'wicket',
                        'player': player_name,
                        'runs': curr_player.get('runs', 0),
                        'balls': curr_player.get('balls', 0),
                        'wicket_info': curr_status
                    })
            
            return wickets
        
        except Exception as e:
            log_error('api_error', 'Wicket detection error', str(e))
            return []
    
    def detect_milestones(self, previous_state, current_state):
        """Milestones detect करो (6, 10, 15, 20 overs)"""
        try:
            milestones = []
            
            prev_over = previous_state.get('overs', {}).get('current_over', 0)
            curr_over = current_state.get('overs', {}).get('current_over', 0)
            
            # Config से milestone list लो
            milestone_list = config.MILESTONES
            
            for milestone in milestone_list:
                if prev_over < milestone <= curr_over:
                    milestones.append({
                        'type': 'milestone',
                        'over': milestone,
                        'description': f'Over {milestone} reached'
                    })
            
            return milestones
        
        except Exception as e:
            log_error('api_error', 'Milestone detection error', str(e))
            return []
    
    def detect_centuries(self, previous_state, current_state):
        """100 runs का century detect करो"""
        try:
            centuries = []
            
            prev_scorecard = previous_state.get('scorecard', {})
            curr_scorecard = current_state.get('scorecard', {})
            
            for curr_player in curr_scorecard.get('team_a', []):
                player_name = curr_player.get('name')
                curr_runs = int(curr_player.get('runs', 0))
                
                prev_player = next((p for p in prev_scorecard.get('team_a', []) 
                                   if p.get('name') == player_name), None)
                prev_runs = int(prev_player.get('runs', 0)) if prev_player else 0
                
                # अगर 100 या उससे ज्यादा है
                if prev_runs < 100 <= curr_runs:
                    centuries.append({
                        'type': 'century',
                        'player': player_name,
                        'runs': curr_runs,
                        'balls': curr_player.get('balls', 0)
                    })
            
            return centuries
        
        except Exception as e:
            log_error('api_error', 'Century detection error', str(e))
            return []
    
    def detect_match_complete(self, current_state):
        """Match complete detect करो"""
        try:
            events = []
            
            status = current_state.get('status', '')
            
            if 'completed' in status.lower() or 'finished' in status.lower():
                winner = current_state.get('winner', 'Unknown')
                
                events.append({
                    'type': 'match_complete',
                    'winner': winner,
                    'description': f'{winner} won!'
                })
            
            return events
        
        except Exception as e:
            log_error('api_error', 'Match complete detection error', str(e))
            return []
    
    def detect_fifty(self, previous_state, current_state):
        """50 runs का fifty detect करो"""
        try:
            fifties = []
            
            prev_scorecard = previous_state.get('scorecard', {})
            curr_scorecard = current_state.get('scorecard', {})
            
            for curr_player in curr_scorecard.get('team_a', []):
                player_name = curr_player.get('name')
                curr_runs = int(curr_player.get('runs', 0))
                
                prev_player = next((p for p in prev_scorecard.get('team_a', []) 
                                   if p.get('name') == player_name), None)
                prev_runs = int(prev_player.get('runs', 0)) if prev_player else 0
                
                # अगर 50 या उससे ज्यादा है लेकिन 100 नहीं है
                if prev_runs < 50 <= curr_runs < 100:
                    fifties.append({
                        'type': 'fifty',
                        'player': player_name,
                        'runs': curr_runs,
                        'balls': curr_player.get('balls', 0)
                    })
            
            return fifties
        
        except Exception as e:
            log_error('api_error', 'Fifty detection error', str(e))
            return []

# Global instance
event_detector = EventDetector()

def detect_all_events(match_id, match_data):
    """किसी भी match में सभी events detect करो"""
    return event_detector.detect_events(match_id, match_data)

def get_event_description(event):
    """Event का description बना"""
    try:
        event_type = event.get('type', '')
        
        if event_type == 'wicket':
            player = event.get('player', 'Player')
            runs = event.get('runs', 0)
            balls = event.get('balls', 0)
            return f"{player} out! ({runs} runs off {balls} balls)"
        
        elif event_type == 'century':
            player = event.get('player', 'Player')
            runs = event.get('runs', 0)
            return f"CENTURY! {player} scores {runs} runs!"
        
        elif event_type == 'fifty':
            player = event.get('player', 'Player')
            runs = event.get('runs', 0)
            return f"FIFTY! {player} reaches {runs} runs!"
        
        elif event_type == 'milestone':
            over = event.get('over', 0)
            return f"Over {over} milestone reached!"
        
        elif event_type == 'match_complete':
            winner = event.get('winner', 'Unknown')
            return f"Match Complete! {winner} wins!"
        
        else:
            return "Cricket event detected!"
    
    except Exception as e:
        log_error('api_error', 'Event description error', str(e))
        return "Event occurred"