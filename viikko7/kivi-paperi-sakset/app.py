import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask, render_template, request, session, redirect, url_for
from luo_peli import LuoPeli
from tuomari import Tuomari
from game_stats import GameStats
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Initialize game statistics
stats = GameStats()

@app.route('/')
def index():
    # Clear session when returning to home page
    session.clear()
    total_games = stats.get_total_games()
    return render_template('index.html', total_games=total_games)

@app.route('/start', methods=['POST'])
def start_game():
    game_type = request.form.get('game_type')
    
    # Initialize game
    peli = LuoPeli.luo_peli(game_type)
    if peli is None:
        return redirect(url_for('index'))
    
    # Store game type and initialize tuomari
    session['game_type'] = game_type
    session['ekan_pisteet'] = 0
    session['tokan_pisteet'] = 0
    session['tasapelit'] = 0
    session['game_over'] = False
    
    # Store AI state for persistence
    if game_type == 'b':
        session['ai_siirto_counter'] = 0
    elif game_type == 'c':
        session['ai_muisti'] = []
    
    return redirect(url_for('play'))

@app.route('/play')
def play():
    if 'game_type' not in session:
        return redirect(url_for('index'))
    
    game_type = session['game_type']
    game_type_names = {
        'a': 'Pelaaja vs Pelaaja',
        'b': 'Pelaaja vs Tekoäly',
        'c': 'Pelaaja vs Parannettu Tekoäly'
    }
    
    return render_template('play.html', 
                         game_type=game_type,
                         game_type_name=game_type_names.get(game_type, 'Tuntematon'),
                         ekan_pisteet=session.get('ekan_pisteet', 0),
                         tokan_pisteet=session.get('tokan_pisteet', 0),
                         tasapelit=session.get('tasapelit', 0),
                         game_over=session.get('game_over', False),
                         winner=session.get('winner'),
                         last_round=session.get('last_round'),
                         total_games=stats.get_total_games())

@app.route('/move', methods=['POST'])
def make_move():
    if 'game_type' not in session or session.get('game_over'):
        return redirect(url_for('index'))
    
    game_type = session['game_type']
    ekan_siirto = request.form.get('ekan_siirto', '').lower()
    
    # Create game instance and restore AI state
    peli = LuoPeli.luo_peli(game_type)
    if game_type == 'b':
        peli._tekoaly._siirto = session.get('ai_siirto_counter', 0)
    elif game_type == 'c':
        saved_moves = session.get('ai_muisti', [])
        # Restore memory: copy saved moves into the fixed-size array
        for i, move in enumerate(saved_moves):
            peli._tekoaly._muisti[i] = move
        peli._tekoaly._vapaa_muisti_indeksi = len(saved_moves)
    
    # Validate first player's move
    if not peli._onko_ok_siirto(ekan_siirto):
        session['game_over'] = True
        session['last_round'] = {
            'ekan_siirto': ekan_siirto,
            'tokan_siirto': '',
            'result': 'Virheellinen siirto! Peli päättyi.'
        }
        return redirect(url_for('play'))
    
    # Get second player's move using game logic
    if game_type == 'a':
        tokan_siirto = request.form.get('tokan_siirto', '').lower()
        if not peli._onko_ok_siirto(tokan_siirto):
            session['game_over'] = True
            session['last_round'] = {
                'ekan_siirto': ekan_siirto,
                'tokan_siirto': tokan_siirto,
                'result': 'Virheellinen siirto! Peli päättyi.'
            }
            return redirect(url_for('play'))
    else:
        # Use the game's AI logic
        tokan_siirto = peli._toisen_siirto(ekan_siirto)
        
        # Update AI memory with player's move (for advanced AI)
        if game_type == 'c':
            peli._tekoaly.aseta_siirto(ekan_siirto)
        
        # Save AI state back to session
        if game_type == 'b':
            session['ai_siirto_counter'] = peli._tekoaly._siirto
        elif game_type == 'c':
            session['ai_muisti'] = peli._tekoaly._muisti[:peli._tekoaly._vapaa_muisti_indeksi]
    
    # Use Tuomari to record move and determine outcome
    tuomari = Tuomari()
    tuomari.ekan_pisteet = session.get('ekan_pisteet', 0)
    tuomari.tokan_pisteet = session.get('tokan_pisteet', 0)
    tuomari.tasapelit = session.get('tasapelit', 0)
    
    # Store previous scores to determine what happened this round
    prev_ekan = tuomari.ekan_pisteet
    prev_tokan = tuomari.tokan_pisteet
    prev_tasapelit = tuomari.tasapelit
    
    # kirjaa_siirto automatically determines tie/winner and updates scores
    tuomari.kirjaa_siirto(ekan_siirto, tokan_siirto)
    
    # Determine what happened by comparing scores
    if tuomari.tasapelit > prev_tasapelit:
        result = "Tasapeli!"
    elif tuomari.ekan_pisteet > prev_ekan:
        result = "Pelaaja 1 voitti kierroksen!"
    else:
        result = "Pelaaja 2 voitti kierroksen!"
    
    session['last_round'] = {
        'ekan_siirto': ekan_siirto,
        'tokan_siirto': tokan_siirto,
        'result': result
    }
    
    # Update session with new scores
    session['ekan_pisteet'] = tuomari.ekan_pisteet
    session['tokan_pisteet'] = tuomari.tokan_pisteet
    session['tasapelit'] = tuomari.tasapelit
    
    # Check if game is over (first to 3 points)
    if tuomari.ekan_pisteet >= 3:
        session['game_over'] = True
        session['winner'] = 'Pelaaja 1'
        stats.increment_game_count(game_type, player1_won=True, player2_won=False)
    elif tuomari.tokan_pisteet >= 3:
        session['game_over'] = True
        session['winner'] = 'Pelaaja 2'
        stats.increment_game_count(game_type, player1_won=False, player2_won=True)
    
    return redirect(url_for('play'))

if __name__ == '__main__':
    app.run(debug=True)
