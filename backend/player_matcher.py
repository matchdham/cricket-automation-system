# ============================================
# FILE: player_matcher.py
# PURPOSE: Fuzzy search + CricAPI player matching
# ============================================

from difflib import SequenceMatcher
from database import fetch_all, fetch_one, log_error
from cricket_api import get_players
import re

class PlayerMatcher:
    """Player को match करो (Fuzzy search)"""
    
    def __init__(self):
        self.local_players = []
        self.cricapi_players = []
        self.load_players()
    
    def load_players(self):
        """Database से सभी players load करो"""
        try:
            self.local_players = fetch_all('SELECT id, name, cricapi_player_id FROM players')
            log_error('success', 'Players loaded')
        except Exception as e:
            log_error('api_error', 'Failed to load players', str(e))
            self.local_players = []
    
    def similarity_score(self, str1, str2):
        """
        दो strings के बीच similarity calculate करो
        
        RETURN:
            float: 0-1 (1 = exact match)
        """
        try:
            # Case-insensitive comparison
            str1_lower = str1.lower().strip()
            str2_lower = str2.lower().strip()
            
            # Exact match
            if str1_lower == str2_lower:
                return 1.0
            
            # Partial match (contains)
            if str1_lower in str2_lower or str2_lower in str1_lower:
                return 0.8
            
            # Fuzzy matching
            matcher = SequenceMatcher(None, str1_lower, str2_lower)
            ratio = matcher.ratio()
            
            return ratio
        
        except Exception as e:
            log_error('api_error', 'Similarity score error', str(e))
            return 0.0
    
    def search_local_players(self, player_name, threshold=0.7):
        """
        Local database में player खोजो
        
        PARAMS:
            player_name: "Virat Kohli"
            threshold: Minimum similarity score (0.7 = 70%)
        
        RETURN:
            list: [matched players]
        """
        try:
            matches = []
            
            if not self.local_players:
                self.load_players()
            
            for player in self.local_players:
                score = self.similarity_score(player_name, player['name'])
                
                if score >= threshold:
                    matches.append({
                        'id': player['id'],
                        'name': player['name'],
                        'cricapi_id': player['cricapi_player_id'],
                        'score': score
                    })
            
            # Score के हिसाब से sort करो (highest first)
            matches.sort(key=lambda x: x['score'], reverse=True)
            
            return matches
        
        except Exception as e:
            log_error('api_error', 'Local player search error', str(e))
            return []
    
    def search_cricapi_players(self, player_name):
        """
        CricAPI में player खोजो
        
        PARAMS:
            player_name: "Virat Kohli"
        
        RETURN:
            list: [CricAPI players]
        """
        try:
            players = get_players(search_term=player_name)
            
            if not players:
                return []
            
            # Top 5 results return करो
            return players[:5]
        
        except Exception as e:
            log_error('api_error', 'CricAPI player search error', str(e))
            return []
    
    def match_player(self, player_name):
        """
        Player को match करो (Local + CricAPI)
        
        STRATEGY:
        1. Local database में 90% से ऊपर match खोजो
        2. नहीं मिले तो CricAPI में खोजो
        3. Both से results return करो
        
        RETURN:
            dict: {local_matches, cricapi_matches}
        """
        try:
            # Local search (high threshold)
            local_matches = self.search_local_players(player_name, threshold=0.9)
            
            # अगर local में exact match मिल गया तो return करो
            if local_matches and local_matches[0]['score'] >= 0.95:
                return {
                    'success': True,
                    'source': 'local',
                    'matches': [local_matches[0]],
                    'exact_match': True
                }
            
            # CricAPI से भी खोजो
            cricapi_matches = self.search_cricapi_players(player_name)
            
            return {
                'success': True,
                'source': 'both',
                'local_matches': local_matches,
                'cricapi_matches': cricapi_matches,
                'exact_match': False
            }
        
        except Exception as e:
            log_error('api_error', 'Player matching error', str(e))
            return {
                'success': False,
                'message': str(e)
            }
    
    def autocomplete_players(self, search_term, limit=10):
        """
        Autocomplete suggestions दो
        
        PARAMS:
            search_term: "Vir" (Virat खोजने के लिए)
            limit: Max results (10)
        
        RETURN:
            list: [suggestions]
        """
        try:
            suggestions = []
            
            if not self.local_players:
                self.load_players()
            
            # Local players से suggestions
            for player in self.local_players:
                if search_term.lower() in player['name'].lower():
                    suggestions.append({
                        'id': player['id'],
                        'name': player['name'],
                        'source': 'local'
                    })
            
            # Limit तक suggestions return करो
            return suggestions[:limit]
        
        except Exception as e:
            log_error('api_error', 'Autocomplete error', str(e))
            return []
    
    def get_player_by_name(self, player_name):
        """
        Exact name से player get करो
        
        RETURN:
            dict: Player info या None
        """
        try:
            player = fetch_one(
                'SELECT * FROM players WHERE LOWER(name) = LOWER(?)',
                (player_name,)
            )
            
            return player
        
        except Exception as e:
            log_error('api_error', 'Get player error', str(e))
            return None
    
    def get_player_by_id(self, player_id):
        """ID से player get करो"""
        try:
            player = fetch_one(
                'SELECT * FROM players WHERE id = ?',
                (player_id,)
            )
            
            return player
        
        except Exception as e:
            log_error('api_error', 'Get player by ID error', str(e))
            return None
    
    def refresh_players(self):
        """Players cache को refresh करो"""
        try:
            self.load_players()
            return {'success': True, 'message': 'Players refreshed'}
        except Exception as e:
            log_error('api_error', 'Refresh players error', str(e))
            return {'success': False, 'message': str(e)}

# Global instance
player_matcher = PlayerMatcher()

def match_player(player_name):
    """Player को match करो"""
    return player_matcher.match_player(player_name)

def search_players(player_name):
    """Players खोजो"""
    return player_matcher.search_local_players(player_name, threshold=0.7)

def autocomplete(search_term):
    """Autocomplete suggestions"""
    return player_matcher.autocomplete_players(search_term)

def get_player(player_name):
    """Player info get करो"""
    return player_matcher.get_player_by_name(player_name)

def refresh():
    """Cache refresh करो"""
    return player_matcher.refresh_players()