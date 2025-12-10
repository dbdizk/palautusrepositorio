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
    
    # For AI games, initialize AI state
    if game_type in ['b', 'c']:
        session['ai_siirto_counter'] = 0
        if game_type == 'c':
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
    
    # Validate first player's move
    if ekan_siirto not in ['k', 'p', 's']:
        session['game_over'] = True
        session['last_round'] = {
            'ekan_siirto': ekan_siirto,
            'tokan_siirto': '',
            'result': 'Virheellinen siirto! Peli päättyi.'
        }
        return redirect(url_for('play'))
    
    # Get second player's move
    if game_type == 'a':
        # Player vs Player
        tokan_siirto = request.form.get('tokan_siirto', '').lower()
        if tokan_siirto not in ['k', 'p', 's']:
            session['game_over'] = True
            session['last_round'] = {
                'ekan_siirto': ekan_siirto,
                'tokan_siirto': tokan_siirto,
                'result': 'Virheellinen siirto! Peli päättyi.'
            }
            return redirect(url_for('play'))
    elif game_type == 'b':
        # Simple AI
        counter = session.get('ai_siirto_counter', 0)
        counter = (counter + 1) % 3
        session['ai_siirto_counter'] = counter
        
        if counter == 0:
            tokan_siirto = "k"
        elif counter == 1:
            tokan_siirto = "p"
        else:
            tokan_siirto = "s"
    else:  # game_type == 'c'
        # Advanced AI
        muisti = session.get('ai_muisti', [])
        
        if len(muisti) == 0 or len(muisti) == 1:
            tokan_siirto = "k"
        else:
            viimeisin_siirto = muisti[-1]
            
            k = 0
            p = 0
            s = 0
            
            for i in range(len(muisti) - 1):
                if viimeisin_siirto == muisti[i]:
                    seuraava = muisti[i + 1]
                    
                    if seuraava == "k":
                        k += 1
                    elif seuraava == "p":
                        p += 1
                    else:
                        s += 1
            
            if k > p or k > s:
                tokan_siirto = "p"
            elif p > k or p > s:
                tokan_siirto = "s"
            else:
                tokan_siirto = "k"
        
        # Update memory
        muisti.append(ekan_siirto)
        if len(muisti) > 10:
            muisti.pop(0)
        session['ai_muisti'] = muisti
    
    # Create tuomari and record move
    tuomari = Tuomari()
    tuomari.ekan_pisteet = session.get('ekan_pisteet', 0)
    tuomari.tokan_pisteet = session.get('tokan_pisteet', 0)
    tuomari.tasapelit = session.get('tasapelit', 0)
    
    tuomari.kirjaa_siirto(ekan_siirto, tokan_siirto)
    
    # Update session
    session['ekan_pisteet'] = tuomari.ekan_pisteet
    session['tokan_pisteet'] = tuomari.tokan_pisteet
    session['tasapelit'] = tuomari.tasapelit
    
    # Check if either player reached 5 points
    winner = None
    if tuomari.ekan_pisteet >= 5:
        session['game_over'] = True
        winner = 'Pelaaja 1'
        # Increment game statistics when game ends
        stats.increment_game_count(game_type, player1_won=True, player2_won=False)
    elif tuomari.tokan_pisteet >= 5:
        session['game_over'] = True
        winner = 'Pelaaja 2'
        # Increment game statistics when game ends
        stats.increment_game_count(game_type, player1_won=False, player2_won=True)
    
    # Determine result
    if ekan_siirto == tokan_siirto:
        result = "Tasapeli!"
    elif tuomari._eka_voittaa(ekan_siirto, tokan_siirto):
        result = "Pelaaja 1 voitti kierroksen!"
    else:
        result = "Pelaaja 2 voitti kierroksen!"
    
    session['last_round'] = {
        'ekan_siirto': ekan_siirto,
        'tokan_siirto': tokan_siirto,
        'result': result
    }
    
    if winner:
        session['winner'] = winner
    
    return redirect(url_for('play'))

if __name__ == '__main__':
    app.run(debug=True)
