import json
import os
from pathlib import Path


class GameStats:
    """Manages game statistics and persists them to a JSON file"""
    
    def __init__(self, stats_file='game_stats.json'):
        self.stats_file = stats_file
        self.stats = self._load_stats()
    
    def _load_stats(self):
        """Load statistics from JSON file, or create default stats if file doesn't exist"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # If file is corrupted, start fresh
                return self._get_default_stats()
        return self._get_default_stats()
    
    def _get_default_stats(self):
        """Return default statistics structure"""
        return {
            'total_games_played': 0,
            'games_by_mode': {
                'a': 0,  # Player vs Player
                'b': 0,  # Player vs AI
                'c': 0   # Player vs Advanced AI
            },
            'total_player1_wins': 0,
            'total_player2_wins': 0
        }
    
    def _save_stats(self):
        """Save current statistics to JSON file"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except IOError as e:
            print(f"Error saving stats: {e}")
    
    def increment_game_count(self, game_mode, player1_won=False, player2_won=False):
        """
        Increment the total games played counter
        
        Args:
            game_mode: 'a', 'b', or 'c' representing the game mode
            player1_won: True if player 1 won this game
            player2_won: True if player 2 won this game
        """
        self.stats['total_games_played'] += 1
        
        if game_mode in self.stats['games_by_mode']:
            self.stats['games_by_mode'][game_mode] += 1
        
        if player1_won:
            self.stats['total_player1_wins'] += 1
        elif player2_won:
            self.stats['total_player2_wins'] += 1
        
        self._save_stats()
    
    def get_total_games(self):
        """Get the total number of games played"""
        return self.stats['total_games_played']
    
    def get_stats(self):
        """Get all statistics"""
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset all statistics to zero"""
        self.stats = self._get_default_stats()
        self._save_stats()
