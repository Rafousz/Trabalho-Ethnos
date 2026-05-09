# app.py
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
from logica_jogo.engine import EthnosGame

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave_secreta_para_desenvolvimento'
socketio = SocketIO(app, cors_allowed_origins="*")

# Armazena as instâncias dos jogos ativos
games = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join_game')
def handle_join(data):
    room = data['room']
    name = data['name']
    
    if room not in games:
        games[room] = EthnosGame(room)
        
    game = games[room]
    success, updated_hands = game.add_player(request.sid, name)
    if success:
        join_room(room)
        for sid, hand in updated_hands.items():
            emit('private_update', {'hand': hand}, to=sid)
        emit('game_update', game.get_public_state(), room=room)
    else:
        emit('error', {'msg': 'Sala cheia!'})

@socketio.on('action_draw_card')
def handle_draw(data):
    room = data['room']
    game = games.get(room)
    
    if game:
        success, updated_hands = game.draw_card(request.sid)
        if success:
            for sid, hand in updated_hands.items():
                emit('private_update', {'hand': hand}, to=sid)
            emit('game_update', game.get_public_state(), room=room)
            return
    
    if game:
        emit('error', {'msg': 'Não é o seu turno ou ação inválida.'}, to=request.sid)
    else:
        emit('error', {'msg': 'Não é o seu turno ou ação inválida.'}, to=request.sid)

@socketio.on('action_draw_market')
def handle_draw_market(data):
    room = data['room']
    index = data.get('index')
    game = games.get(room)
    
    if game:
        success, updated_hands = game.draw_market_card(request.sid, index)
        if success:
            for sid, hand in updated_hands.items():
                emit('private_update', {'hand': hand}, to=sid)
            emit('game_update', game.get_public_state(), room=room)
            return
    
    if game:
        emit('error', {'msg': 'Não é o seu turno ou carta inválida.'}, to=request.sid)
    else:
        emit('error', {'msg': 'Não é o seu turno ou carta inválida.'}, to=request.sid)

@socketio.on('action_play_band')
def handle_play_band(data):
    room = data['room']
    indices = data.get('indices', [])
    game = games.get(room)
    
    if game:
        success, msg = game.play_band(request.sid, indices)
        if success:
            emit('private_update', {'hand': game.players[request.sid].hand}, to=request.sid)
            emit('game_update', game.get_public_state(), room=room)
        else:
            emit('error', {'msg': msg}, to=request.sid)

if __name__ == '__main__':
    socketio.run(app, debug=True)