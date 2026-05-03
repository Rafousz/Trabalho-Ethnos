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
    if game.add_player(request.sid, name):
        join_room(room)
        emit('game_update', game.get_public_state(), room=room)
    else:
        emit('error', {'msg': 'Sala cheia!'})

@socketio.on('action_draw_card')
def handle_draw(data):
    room = data['room']
    game = games.get(room)
    
    if game and game.draw_card(request.sid):
        emit('private_update', {'hand': game.players[request.sid].hand}, to=request.sid)
        emit('game_update', game.get_public_state(), room=room)
    else:
        emit('error', {'msg': 'Não é o seu turno ou ação inválida.'}, to=request.sid)

if __name__ == '__main__':
    socketio.run(app, debug=True)