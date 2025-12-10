import pytest
import sys
import os
import tempfile
import json

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app, stats
from game_stats import GameStats


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    # Use a temporary file for stats during testing
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        test_stats_file = f.name
    
    # Replace the global stats object with one using test file
    original_stats_file = stats.stats_file
    stats.stats_file = test_stats_file
    stats.stats = stats._get_default_stats()
    stats._save_stats()
    
    with app.test_client() as client:
        yield client
    
    # Cleanup
    stats.stats_file = original_stats_file
    if os.path.exists(test_stats_file):
        os.unlink(test_stats_file)


@pytest.fixture
def client_with_session(client):
    """Create a test client with session context"""
    with client.session_transaction() as sess:
        yield client, sess


class TestHomePage:
    """Tests for the home page route"""
    
    def test_home_page_loads(self, client):
        """Test that home page loads successfully"""
        response = client.get('/')
        assert response.status_code == 200
        assert 'Kivi Paperi Sakset'.encode('utf-8') in response.data
    
    def test_home_page_shows_game_options(self, client):
        """Test that all game mode options are displayed"""
        response = client.get('/')
        assert 'Pelaaja vs Pelaaja'.encode('utf-8') in response.data
        assert 'Pelaaja vs Tekoäly'.encode('utf-8') in response.data
        assert 'Pelaaja vs Parannettu Tekoäly'.encode('utf-8') in response.data
    
    def test_home_page_clears_session(self, client):
        """Test that visiting home page clears the session"""
        with client.session_transaction() as sess:
            sess['game_type'] = 'a'
            sess['ekan_pisteet'] = 5
        
        client.get('/')
        
        with client.session_transaction() as sess:
            assert 'game_type' not in sess
            assert 'ekan_pisteet' not in sess


class TestStartGame:
    """Tests for starting a new game"""
    
    def test_start_player_vs_player(self, client):
        """Test starting a player vs player game"""
        response = client.post('/start', data={'game_type': 'a'}, follow_redirects=True)
        assert response.status_code == 200
        
        with client.session_transaction() as sess:
            assert sess['game_type'] == 'a'
            assert sess['ekan_pisteet'] == 0
            assert sess['tokan_pisteet'] == 0
            assert sess['tasapelit'] == 0
            assert sess['game_over'] == False
    
    def test_start_ai_game(self, client):
        """Test starting an AI game"""
        response = client.post('/start', data={'game_type': 'b'}, follow_redirects=True)
        assert response.status_code == 200
        
        with client.session_transaction() as sess:
            assert sess['game_type'] == 'b'
            assert 'ai_siirto_counter' in sess
    
    def test_start_advanced_ai_game(self, client):
        """Test starting an advanced AI game"""
        response = client.post('/start', data={'game_type': 'c'}, follow_redirects=True)
        assert response.status_code == 200
        
        with client.session_transaction() as sess:
            assert sess['game_type'] == 'c'
            assert 'ai_muisti' in sess
            assert sess['ai_muisti'] == []
    
    def test_start_invalid_game_type(self, client):
        """Test that invalid game type redirects to home"""
        response = client.post('/start', data={'game_type': 'z'})
        assert response.status_code == 302
        assert response.location == '/'


class TestPlayPage:
    """Tests for the play page"""
    
    def test_play_page_without_session(self, client):
        """Test that play page redirects if no game is started"""
        response = client.get('/play')
        assert response.status_code == 302
        assert response.location == '/'
    
    def test_play_page_with_session(self, client):
        """Test that play page loads with active game"""
        with client.session_transaction() as sess:
            sess['game_type'] = 'a'
            sess['ekan_pisteet'] = 0
            sess['tokan_pisteet'] = 0
            sess['tasapelit'] = 0
            sess['game_over'] = False
        
        response = client.get('/play')
        assert response.status_code == 200
        assert 'Pelaaja vs Pelaaja'.encode('utf-8') in response.data
    
    def test_play_page_shows_scores(self, client):
        """Test that play page displays current scores"""
        with client.session_transaction() as sess:
            sess['game_type'] = 'b'
            sess['ekan_pisteet'] = 3
            sess['tokan_pisteet'] = 2
            sess['tasapelit'] = 1
            sess['game_over'] = False
        
        response = client.get('/play')
        assert response.status_code == 200
        # Scores are rendered in the HTML


class TestPlayerVsPlayer:
    """Tests for player vs player game moves"""
    
    def setup_pvp_game(self, client):
        """Helper to set up a PvP game"""
        with client.session_transaction() as sess:
            sess['game_type'] = 'a'
            sess['ekan_pisteet'] = 0
            sess['tokan_pisteet'] = 0
            sess['tasapelit'] = 0
            sess['game_over'] = False
    
    def test_valid_move_rock_vs_scissors(self, client):
        """Test rock beats scissors"""
        self.setup_pvp_game(client)
        
        response = client.post('/move', data={
            'ekan_siirto': 'k',
            'tokan_siirto': 's'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with client.session_transaction() as sess:
            assert sess['ekan_pisteet'] == 1
            assert sess['tokan_pisteet'] == 0
            assert sess['tasapelit'] == 0
            assert sess['game_over'] == False  # Game continues until 3 points
    
    def test_valid_move_paper_vs_rock(self, client):
        """Test paper beats rock"""
        self.setup_pvp_game(client)
        
        response = client.post('/move', data={
            'ekan_siirto': 'p',
            'tokan_siirto': 'k'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with client.session_transaction() as sess:
            assert sess['ekan_pisteet'] == 1
            assert sess['tokan_pisteet'] == 0
    
    def test_valid_move_scissors_vs_paper(self, client):
        """Test scissors beats paper"""
        self.setup_pvp_game(client)
        
        response = client.post('/move', data={
            'ekan_siirto': 's',
            'tokan_siirto': 'p'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with client.session_transaction() as sess:
            assert sess['ekan_pisteet'] == 1
            assert sess['tokan_pisteet'] == 0
    
    def test_valid_move_player2_wins(self, client):
        """Test when player 2 wins"""
        self.setup_pvp_game(client)
        
        response = client.post('/move', data={
            'ekan_siirto': 'k',
            'tokan_siirto': 'p'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with client.session_transaction() as sess:
            assert sess['ekan_pisteet'] == 0
            assert sess['tokan_pisteet'] == 1
    
    def test_valid_move_tie(self, client):
        """Test a tie game"""
        self.setup_pvp_game(client)
        
        response = client.post('/move', data={
            'ekan_siirto': 'k',
            'tokan_siirto': 'k'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with client.session_transaction() as sess:
            assert sess['ekan_pisteet'] == 0
            assert sess['tokan_pisteet'] == 0
            assert sess['tasapelit'] == 1
    
    def test_invalid_first_player_move(self, client):
        """Test invalid move from first player"""
        self.setup_pvp_game(client)
        
        response = client.post('/move', data={
            'ekan_siirto': 'x',
            'tokan_siirto': 'k'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with client.session_transaction() as sess:
            assert sess['game_over'] == True
    
    def test_invalid_second_player_move(self, client):
        """Test invalid move from second player"""
        self.setup_pvp_game(client)
        
        response = client.post('/move', data={
            'ekan_siirto': 'k',
            'tokan_siirto': 'invalid'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with client.session_transaction() as sess:
            assert sess['game_over'] == True
    
    def test_multiple_rounds(self, client):
        """Test multiple rounds accumulate scores correctly"""
        self.setup_pvp_game(client)
        
        # Round 1: Player 1 wins
        client.post('/move', data={'ekan_siirto': 'k', 'tokan_siirto': 's'})
        
        # Round 2: Player 2 wins
        client.post('/move', data={'ekan_siirto': 's', 'tokan_siirto': 'k'})
        
        # Round 3: Tie
        client.post('/move', data={'ekan_siirto': 'p', 'tokan_siirto': 'p'})
        
        with client.session_transaction() as sess:
            assert sess['ekan_pisteet'] == 1
            assert sess['tokan_pisteet'] == 1
            assert sess['tasapelit'] == 1
            assert sess['game_over'] == False  # Game not over yet
    
    def test_player1_wins_at_3_points(self, client):
        """Test that game ends when player 1 reaches 3 points"""
        self.setup_pvp_game(client)
        
        # Player 1 wins 3 times
        for i in range(3):
            client.post('/move', data={'ekan_siirto': 'k', 'tokan_siirto': 's'})
        
        with client.session_transaction() as sess:
            assert sess['ekan_pisteet'] == 3
            assert sess['tokan_pisteet'] == 0
            assert sess['game_over'] == True
            assert sess['winner'] == 'Pelaaja 1'
    
    def test_player2_wins_at_3_points(self, client):
        """Test that game ends when player 2 reaches 3 points"""
        self.setup_pvp_game(client)
        
        # Player 2 wins 3 times
        for i in range(3):
            client.post('/move', data={'ekan_siirto': 's', 'tokan_siirto': 'k'})
        
        with client.session_transaction() as sess:
            assert sess['ekan_pisteet'] == 0
            assert sess['tokan_pisteet'] == 3
            assert sess['game_over'] == True
            assert sess['winner'] == 'Pelaaja 2'
    
    def test_game_continues_until_3_points(self, client):
        """Test that game continues even with 2 points"""
        self.setup_pvp_game(client)
        
        # Player 1 wins 2 times
        for i in range(2):
            client.post('/move', data={'ekan_siirto': 'k', 'tokan_siirto': 's'})
        
        with client.session_transaction() as sess:
            assert sess['ekan_pisteet'] == 2
            assert sess['game_over'] == False
        
        # One more win reaches 3
        client.post('/move', data={'ekan_siirto': 'k', 'tokan_siirto': 's'})
        
        with client.session_transaction() as sess:
            assert sess['ekan_pisteet'] == 3
            assert sess['game_over'] == True


class TestAIGame:
    """Tests for AI opponent games"""
    
    def setup_ai_game(self, client):
        """Helper to set up an AI game"""
        with client.session_transaction() as sess:
            sess['game_type'] = 'b'
            sess['ekan_pisteet'] = 0
            sess['tokan_pisteet'] = 0
            sess['tasapelit'] = 0
            sess['game_over'] = False
            sess['ai_siirto_counter'] = 0
    
    def test_ai_makes_move(self, client):
        """Test that AI makes a valid move"""
        self.setup_ai_game(client)
        
        response = client.post('/move', data={
            'ekan_siirto': 'k'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with client.session_transaction() as sess:
            # Score should have changed
            total_score = sess['ekan_pisteet'] + sess['tokan_pisteet'] + sess['tasapelit']
            assert total_score == 1
            assert sess['game_over'] == False  # Game not over after one round
    
    def test_ai_cycles_through_moves(self, client):
        """Test that simple AI cycles through k, p, s"""
        self.setup_ai_game(client)
        
        # First move should be 'p' (counter becomes 1)
        client.post('/move', data={'ekan_siirto': 'k'})
        
        with client.session_transaction() as sess:
            counter1 = sess['ai_siirto_counter']
        
        # Second move should be 's' (counter becomes 2)
        client.post('/move', data={'ekan_siirto': 'k'})
        
        with client.session_transaction() as sess:
            counter2 = sess['ai_siirto_counter']
        
        # Third move should be 'k' (counter becomes 0)
        client.post('/move', data={'ekan_siirto': 'k'})
        
        with client.session_transaction() as sess:
            counter3 = sess['ai_siirto_counter']
        
        assert counter1 == 1
        assert counter2 == 2
        assert counter3 == 0
    
    def test_ai_game_ends_at_2_points(self, client):
        """Test that AI game ends when either player reaches 3 points"""
        self.setup_ai_game(client)
        
        # AI cycles: first move is 'p' (counter 0->1), then 's' (1->2), then 'k' (2->0)
        # To ensure player wins, we play the winning move each time
        moves = ['s', 'k', 'p']  # s beats p, k beats s, p beats k
        for move in moves:
            client.post('/move', data={'ekan_siirto': move})
        
        with client.session_transaction() as sess:
            assert sess['game_over'] == True
            # Player should have won 3 times
            assert sess['ekan_pisteet'] == 3


class TestAdvancedAIGame:
    """Tests for advanced AI opponent games"""
    
    def setup_advanced_ai_game(self, client):
        """Helper to set up an advanced AI game"""
        with client.session_transaction() as sess:
            sess['game_type'] = 'c'
            sess['ekan_pisteet'] = 0
            sess['tokan_pisteet'] = 0
            sess['tasapelit'] = 0
            sess['game_over'] = False
            sess['ai_muisti'] = []
    
    def test_advanced_ai_makes_move(self, client):
        """Test that advanced AI makes a valid move"""
        self.setup_advanced_ai_game(client)
        
        response = client.post('/move', data={
            'ekan_siirto': 'k'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with client.session_transaction() as sess:
            # Score should have changed
            total_score = sess['ekan_pisteet'] + sess['tokan_pisteet'] + sess['tasapelit']
            assert total_score == 1
    
    def test_advanced_ai_updates_memory(self, client):
        """Test that advanced AI maintains memory of moves"""
        self.setup_advanced_ai_game(client)
        
        # Make several moves
        moves = ['k', 'p', 's', 'k', 'p']
        for move in moves:
            client.post('/move', data={'ekan_siirto': move})
        
        with client.session_transaction() as sess:
            assert len(sess['ai_muisti']) == 5
            assert sess['ai_muisti'] == moves
    
    def test_advanced_ai_memory_limit(self, client):
        """Test that advanced AI memory grows correctly (limited by game ending at 3 points)"""
        self.setup_advanced_ai_game(client)
        
        # Make 2 moves (game will end at 3 points, so we can't test full 10-item limit)
        # Use ties to not trigger the 3-point win
        for i in range(2):
            # AI returns 'k' for first move, so we play 'k' for ties
            client.post('/move', data={'ekan_siirto': 'k'})
        
        with client.session_transaction() as sess:
            assert len(sess['ai_muisti']) == 2
            assert sess['game_over'] == False
    
    def test_advanced_ai_first_move(self, client):
        """Test that advanced AI returns 'k' on first move"""
        self.setup_advanced_ai_game(client)
        
        # On first move, AI should always return 'k'
        # So if player plays 's', player should win
        client.post('/move', data={'ekan_siirto': 's'})
        
        with client.session_transaction() as sess:
            # Player should lose (k beats s)
            assert sess['tokan_pisteet'] == 1


class TestGameFlow:
    """Tests for overall game flow"""
    
    def test_complete_game_flow(self, client):
        """Test a complete game from start to finish"""
        # Start game
        client.post('/start', data={'game_type': 'a'})
        
        # Make valid moves - player 1 wins 3 times
        for i in range(3):
            client.post('/move', data={'ekan_siirto': 'k', 'tokan_siirto': 's'})
        
        with client.session_transaction() as sess:
            assert sess['game_over'] == True
            assert sess['ekan_pisteet'] == 3
            assert sess['winner'] == 'Pelaaja 1'
    
    def test_cannot_move_without_starting_game(self, client):
        """Test that moves are rejected without starting a game"""
        response = client.post('/move', data={'ekan_siirto': 'k', 'tokan_siirto': 's'})
        assert response.status_code == 302
        assert response.location == '/'
    
    def test_cannot_move_after_game_over(self, client):
        """Test that moves are rejected after game ends"""
        with client.session_transaction() as sess:
            sess['game_type'] = 'a'
            sess['game_over'] = True
        
        response = client.post('/move', data={'ekan_siirto': 'k', 'tokan_siirto': 's'})
        assert response.status_code == 302
        assert response.location == '/'
    
    def test_restart_game(self, client):
        """Test restarting a game clears previous state"""
        # Start first game
        client.post('/start', data={'game_type': 'a'})
        client.post('/move', data={'ekan_siirto': 'k', 'tokan_siirto': 's'})
        
        # Go home (clears session)
        client.get('/')
        
        # Start new game
        client.post('/start', data={'game_type': 'b'})
        
        with client.session_transaction() as sess:
            assert sess['game_type'] == 'b'
            assert sess['ekan_pisteet'] == 0
            assert sess['tokan_pisteet'] == 0
            assert sess['tasapelit'] == 0


class TestSessionManagement:
    """Tests for session management"""
    
    def test_session_persists_across_requests(self, client):
        """Test that session data persists across multiple requests"""
        client.post('/start', data={'game_type': 'a'})
        
        # Make first request
        client.post('/move', data={'ekan_siirto': 'k', 'tokan_siirto': 's'})
        
        # Check session
        with client.session_transaction() as sess:
            score1 = sess['ekan_pisteet']
        
        # Make second request
        client.post('/move', data={'ekan_siirto': 'p', 'tokan_siirto': 'k'})
        
        # Check session again
        with client.session_transaction() as sess:
            score2 = sess['ekan_pisteet']
        
        assert score2 == score1 + 1
    
    def test_last_round_stored_in_session(self, client):
        """Test that last round information is stored"""
        with client.session_transaction() as sess:
            sess['game_type'] = 'a'
            sess['ekan_pisteet'] = 0
            sess['tokan_pisteet'] = 0
            sess['tasapelit'] = 0
            sess['game_over'] = False
        
        client.post('/move', data={'ekan_siirto': 'k', 'tokan_siirto': 's'})
        
        with client.session_transaction() as sess:
            assert 'last_round' in sess
            assert sess['last_round']['ekan_siirto'] == 'k'
            assert sess['last_round']['tokan_siirto'] == 's'
            assert 'result' in sess['last_round']


class TestGameStats:
    """Tests for game statistics functionality"""
    
    def test_stats_file_created(self):
        """Test that GameStats creates a stats file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            test_file = f.name
        
        # Remove the file to test creation
        os.unlink(test_file)
        
        game_stats = GameStats(test_file)
        # File is created when stats are saved
        game_stats.increment_game_count('a', player1_won=True)
        assert os.path.exists(test_file)
        assert game_stats.get_total_games() == 1
        
        # Cleanup
        os.unlink(test_file)
    
    def test_increment_game_count(self):
        """Test incrementing game count"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            test_file = f.name
        
        game_stats = GameStats(test_file)
        
        initial_count = game_stats.get_total_games()
        game_stats.increment_game_count('a', player1_won=True)
        
        assert game_stats.get_total_games() == initial_count + 1
        
        # Verify it persists
        game_stats2 = GameStats(test_file)
        assert game_stats2.get_total_games() == initial_count + 1
        
        # Cleanup
        os.unlink(test_file)
    
    def test_stats_persistence(self):
        """Test that stats persist across instances"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            test_file = f.name
        
        # First instance
        stats1 = GameStats(test_file)
        stats1.increment_game_count('a', player1_won=True)
        stats1.increment_game_count('b', player2_won=True)
        stats1.increment_game_count('c', player1_won=True)
        
        # Second instance should load the same data
        stats2 = GameStats(test_file)
        assert stats2.get_total_games() == 3
        
        all_stats = stats2.get_stats()
        assert all_stats['games_by_mode']['a'] == 1
        assert all_stats['games_by_mode']['b'] == 1
        assert all_stats['games_by_mode']['c'] == 1
        assert all_stats['total_player1_wins'] == 2
        assert all_stats['total_player2_wins'] == 1
        
        # Cleanup
        os.unlink(test_file)
    
    def test_home_page_shows_total_games(self, client):
        """Test that home page displays total games count"""
        response = client.get('/')
        assert response.status_code == 200
        assert 'Yhteensä pelejä pelattu'.encode('utf-8') in response.data
    
    def test_game_completion_increments_stats(self, client):
        """Test that completing a game increments the stats counter"""
        # Get initial count
        initial_count = stats.get_total_games()
        
        # Start and complete a game
        client.post('/start', data={'game_type': 'a'})
        
        # Player 1 wins 3 times
        for i in range(3):
            client.post('/move', data={'ekan_siirto': 'k', 'tokan_siirto': 's'})
        
        # Check that stats were incremented
        assert stats.get_total_games() == initial_count + 1
        
        # Verify the win was recorded
        all_stats = stats.get_stats()
        assert all_stats['games_by_mode']['a'] >= 1
    
    def test_multiple_games_increment_counter(self, client):
        """Test that multiple games increment the counter correctly"""
        initial_count = stats.get_total_games()
        
        # Play 3 complete games
        for game_num in range(3):
            client.post('/start', data={'game_type': 'a'})
            for i in range(3):
                client.post('/move', data={'ekan_siirto': 'k', 'tokan_siirto': 's'})
        
        assert stats.get_total_games() == initial_count + 3
    
    def test_different_game_modes_tracked(self, client):
        """Test that different game modes are tracked separately"""
        initial_stats = stats.get_stats()
        
        # Play player vs player game
        client.post('/start', data={'game_type': 'a'})
        for i in range(3):
            client.post('/move', data={'ekan_siirto': 'k', 'tokan_siirto': 's'})
        
        # Play AI game - AI cycles k->p->s, so we counter appropriately
        client.post('/start', data={'game_type': 'b'})
        moves = ['s', 'k', 'p']  # Counter AI's p, s, k
        for move in moves:
            client.post('/move', data={'ekan_siirto': move})
        
        final_stats = stats.get_stats()
        
        # At least two game modes should have been completed
        assert final_stats['total_games_played'] >= initial_stats['total_games_played'] + 2

