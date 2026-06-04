import requests
from .config import config

BASE_URL = "https://api.cricapi.com/v1"
CRICAPI_KEY = "26d7de00-35e1-47a8-aea7-54b76903ba57"

# ============================================
# CURRENT & LIVE MATCHES
# ============================================

def get_current_matches():
    """Get all current/live matches"""
    try:
        url = f"{BASE_URL}/currentMatches"
        params = {
            'apikey': API_KEY,
            'offset': 0
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('data', []) if data.get('status') == 'ok' else []
    except Exception as e:
        print(f"Error fetching current matches: {e}")
        return []

def get_all_matches():
    """Get all matches"""
    try:
        url = f"{BASE_URL}/matches"
        params = {
            'apikey': API_KEY,
            'offset': 0
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('data', []) if data.get('status') == 'ok' else []
    except Exception as e:
        print(f"Error fetching all matches: {e}")
        return []

# ============================================
# MATCH INFO & DETAILS
# ============================================

def get_match_info(match_id):
    """Get detailed match information"""
    try:
        url = f"{BASE_URL}/match_info"
        params = {
            'apikey': API_KEY,
            'id': match_id
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('data', {}) if data.get('status') == 'ok' else {}
    except Exception as e:
        print(f"Error fetching match info: {e}")
        return {}

# ============================================
# COUNTRIES & SERIES
# ============================================

def get_countries():
    """Get list of countries with flags"""
    try:
        url = f"{BASE_URL}/countries"
        params = {
            'apikey': API_KEY,
            'offset': 0
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('data', []) if data.get('status') == 'ok' else []
    except Exception as e:
        print(f"Error fetching countries: {e}")
        return []

def get_series_list(offset=0):
    """Get cricket series list"""
    try:
        url = f"{BASE_URL}/series"
        params = {
            'apikey': API_KEY,
            'offset': offset
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('data', []) if data.get('status') == 'ok' else []
    except Exception as e:
        print(f"Error fetching series list: {e}")
        return []

def search_series(search_query):
    """Search cricket series by name (e.g., 'IPL')"""
    try:
        url = f"{BASE_URL}/series"
        params = {
            'apikey': API_KEY,
            'offset': 0,
            'search': search_query
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('data', []) if data.get('status') == 'ok' else []
    except Exception as e:
        print(f"Error searching series: {e}")
        return []

def get_series_info(series_id):
    """Get detailed series information"""
    try:
        url = f"{BASE_URL}/series_info"
        params = {
            'apikey': API_KEY,
            'id': series_id
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('data', {}) if data.get('status') == 'ok' else {}
    except Exception as e:
        print(f"Error fetching series info: {e}")
        return {}

# ============================================
# PLAYERS
# ============================================

def get_all_players(offset=0):
    """Get all players list"""
    try:
        url = f"{BASE_URL}/players"
        params = {
            'apikey': API_KEY,
            'offset': offset
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('data', []) if data.get('status') == 'ok' else []
    except Exception as e:
        print(f"Error fetching all players: {e}")
        return []

def search_players(player_name):
    """Search players by name"""
    try:
        url = f"{BASE_URL}/players"
        params = {
            'apikey': API_KEY,
            'offset': 0,
            'search': player_name
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('data', []) if data.get('status') == 'ok' else []
    except Exception as e:
        print(f"Error searching players: {e}")
        return []

def get_player_info(player_id):
    """Get detailed player information"""
    try:
        url = f"{BASE_URL}/players_info"
        params = {
            'apikey': API_KEY,
            'id': player_id
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('data', {}) if data.get('status') == 'ok' else {}
    except Exception as e:
        print(f"Error fetching player info: {e}")
        return {}

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_live_score(match_id):
    """Get live score for a match"""
    match_data = get_match_info(match_id)
    if match_data:
        return {
            'match_id': match_id,
            'status': match_data.get('status', 'Unknown'),
            'team1': match_data.get('teams', {}).get('team1', ''),
            'team2': match_data.get('teams', {}).get('team2', ''),
            'score': match_data.get('score', {}),
            'description': match_data.get('description', ''),
            'updated': match_data.get('updated', '')
        }
    return None

def get_match_summary():
    """Get summary of all current matches"""
    matches = get_current_matches()
    summary = {
        'total_matches': len(matches),
        'matches': []
    }
    
    for match in matches:
        summary['matches'].append({
            'id': match.get('id'),
            'name': match.get('name'),
            'status': match.get('status'),
            'teams': match.get('teams'),
            'score': match.get('score')
        })
    
    return summary

def get_team_players(team_name):
    """Search players from a specific team"""
    all_players = get_all_players()
    team_players = [p for p in all_players if team_name.lower() in p.get('name', '').lower()]
    return team_players

# ============================================
# CRICKET DATA UTILITIES
# ============================================

def format_match_data(match):
    """Format match data for display"""
    return {
        'id': match.get('id'),
        'name': match.get('name'),
        'status': match.get('status'),
        'status_str': match.get('status_str'),
        'team1': match.get('teams', {}).get('team1'),
        'team2': match.get('teams', {}).get('team2'),
        'score_team1': match.get('score', {}).get('team1'),
        'score_team2': match.get('score', {}).get('team2'),
        'description': match.get('description'),
        'updated': match.get('updated')
    }

def format_player_data(player):
    """Format player data for display"""
    return {
        'id': player.get('id'),
        'name': player.get('name'),
        'role': player.get('role'),
        'country': player.get('country'),
        'image': player.get('image')
    }

def get_match_updates():
    """Get all match updates and live data"""
    matches = get_current_matches()
    return [format_match_data(m) for m in matches]
