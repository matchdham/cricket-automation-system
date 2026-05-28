# ============================================
# FILE: cricket_api.py
# PURPOSE: CricAPI integration - Live data fetch
# ============================================

import requests
from config import config
from database import log_error

CRICAPI_KEY = config.CRICAPI_KEY
BASE_URL = config.CRICAPI_BASE_URL

def get_current_matches():
    """
    CricAPI से सभी live + upcoming matches fetch करो
    
    RETURN:
        list: [{match_id, name, status, score, ...}, ...]
    """
    try:
        url = f"{BASE_URL}/currentMatches"
        params = {"apikey": CRICAPI_KEY}
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            log_error("cricapi_error", f"currentMatches failed: {response.status_code}")
            return []
        
        data = response.json()
        matches = data.get("data", [])
        
        log_error('success', f'Fetched {len(matches)} matches')
        
        return matches
        
    except requests.exceptions.RequestException as e:
        log_error('cricapi_error', 'currentMatches failed', str(e))
        return []
    except Exception as e:
        log_error('api_error', 'currentMatches error', str(e))
        return []

def get_match_info(match_id):
    """
    एक match का detailed info fetch करो
    (Over, runs, wickets, fall_of_wickets, etc)
    
    PARAMS:
        match_id: Match का unique ID
    
    RETURN:
        dict: {over, runs, wickets, scorecard, ...}
    """
    try:
        url = f"{BASE_URL}/match_info"
        params = {
            "apikey": CRICAPI_KEY,
            "id": match_id
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            log_error("cricapi_error", f"match_info failed: {response.status_code}")
            return None
        
        data = response.json()
        match_data = data.get("data", {})
        
        log_error('success', f'Fetched match info: {match_id}')
        
        return match_data
        
    except requests.exceptions.RequestException as e:
        log_error('cricapi_error', 'match_info failed', str(e))
        return None
    except Exception as e:
        log_error('api_error', 'match_info error', str(e))
        return None

def get_series(search_term=None):
    """
    Cricket series list fetch करो (IPL, T20, etc)
    
    PARAMS:
        search_term: Optional - "IPL" search करने के लिए
    
    RETURN:
        list: [{series_id, name, status}, ...]
    """
    try:
        url = f"{BASE_URL}/series"
        params = {"apikey": CRICAPI_KEY}
        
        if search_term:
            params["search"] = search_term
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        series = data.get("data", [])
        
        return series
        
    except Exception as e:
        log_error('api_error', 'series fetch error', str(e))
        return []

def get_players(search_term=None):
    """
    Players list fetch करो (Autocomplete के लिए)
    
    PARAMS:
        search_term: Optional - Player name search करने के लिए
    
    RETURN:
        list: [{player_id, name, country}, ...]
    """
    try:
        url = f"{BASE_URL}/players"
        params = {"apikey": CRICAPI_KEY}
        
        if search_term:
            params["search"] = search_term
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        players = data.get("data", [])
        
        return players
        
    except Exception as e:
        log_error('api_error', 'players fetch error', str(e))
        return []

def detect_wickets(previous_match_data, current_match_data):
    """
    पिछले match data और current data को compare करके
    नए wickets detect करो
    
    PARAMS:
        previous_match_data: पिछली call का data
        current_match_data: इस call का data
    
    RETURN:
        list: [नए wickets]
    """
    try:
        new_wickets = []
        
        if not previous_match_data or not current_match_data:
            return new_wickets
        
        prev_scorecard = previous_match_data.get('scorecard', {}).get('team_a', [])
        curr_scorecard = current_match_data.get('scorecard', {}).get('team_a', [])
        
        for player in curr_scorecard:
            player_name = player.get('name')
            curr_wicket = player.get('wicket')
            
            # पिछली call में player को खोजो
            prev_player = next((p for p in prev_scorecard if p.get('name') == player_name), None)
            prev_wicket = prev_player.get('wicket') if prev_player else None
            
            # अगर पहले "not out" था और अब कोई wicket है, तो नया wicket है
            if prev_wicket == "not out" and curr_wicket and curr_wicket != "not out":
                new_wickets.append({
                    'player': player_name,
                    'wicket_info': curr_wicket,
                    'runs': player.get('runs'),
                    'balls': player.get('balls')
                })
        
        return new_wickets
        
    except Exception as e:
        log_error('api_error', 'wicket detection error', str(e))
        return []

def detect_milestone(previous_score, current_score, milestones=[50, 100]):
    """
    Milestone detect करो (50, 100 runs, etc)
    
    PARAMS:
        previous_score: पिछला score
        current_score: अब का score
        milestones: List of milestone numbers
    
    RETURN:
        list: [नए milestones]
    """
    try:
        new_milestones = []
        
        if not previous_score or not current_score:
            return new_milestones
        
        prev_runs = int(previous_score)
        curr_runs = int(current_score)
        
        for milestone in milestones:
            if prev_runs < milestone <= curr_runs:
                new_milestones.append(milestone)
        
        return new_milestones
        
    except Exception as e:
        log_error('api_error', 'milestone detection error', str(e))
        return []