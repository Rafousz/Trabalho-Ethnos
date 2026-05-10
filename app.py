# app.py
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
from logica_jogo.engine import EthnosGame

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave_secreta_para_desenvolvimento'
socketio = SocketIO(app, cors_allowed_origins="*")

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
        success, result = game.draw_card(request.sid)
        if success:
            for sid, hand in result.items():
                emit('private_update', {'hand': hand}, to=sid)
            emit('game_update', game.get_public_state(), room=room)
        else:
            emit('error', {'msg': result}, to=request.sid)
    else:
        emit('error', {'msg': 'Jogo não encontrado.'}, to=request.sid)

@socketio.on('action_draw_market')
def handle_draw_market(data):
    room = data['room']
    index = data.get('index')
    game = games.get(room)

    if game:
        success, result = game.draw_market_card(request.sid, index)
        if success:
            for sid, hand in result.items():
                emit('private_update', {'hand': hand}, to=sid)
            emit('game_update', game.get_public_state(), room=room)
        else:
            emit('error', {'msg': result}, to=request.sid)
    else:
        emit('error', {'msg': 'Jogo não encontrado.'}, to=request.sid)

@socketio.on('action_play_band')
def handle_play_band(data):
    room = data['room']
    indices = data.get('indices', [])
    game = games.get(room)

    if game:
        success, msg, updated_hands = game.play_band(request.sid, indices)
        if success:
            if msg == 'PENDING_GUERREIROS':
                # Pede ao jogador para escolher o reino
                emit('choose_realm', {
                    'realms': list(game.glory_tokens.keys())
                }, to=request.sid)
                emit('game_update', game.get_public_state(), room=room)
            elif msg == 'PENDING_ELFOS':
                # Pede ao jogador para escolher quais cartas manter
                pending = game.pending_action
                emit('choose_keep_cards', {
                    'cards': pending['remaining_cards'],
                    'n_manter': pending['n_manter'],
                }, to=request.sid)
                emit('private_update', {'hand': []}, to=request.sid)
                emit('game_update', game.get_public_state(), room=room)
            else:
                if updated_hands:
                    for sid, hand in updated_hands.items():
                        emit('private_update', {'hand': hand}, to=sid)
                emit('game_update', game.get_public_state(), room=room)
        else:
            emit('error', {'msg': msg}, to=request.sid)

@socketio.on('action_choose_realm')
def handle_choose_realm(data):
    """Recebe a escolha de reino do jogador Guerreiro."""
    room = data['room']
    realm = data.get('realm')
    game = games.get(room)

    if game:
        success, msg, updated_hands = game.resolve_guerreiros(request.sid, realm)
        if success:
            if updated_hands:
                for sid, hand in updated_hands.items():
                    emit('private_update', {'hand': hand}, to=sid)
            emit('game_update', game.get_public_state(), room=room)
        else:
            emit('error', {'msg': msg}, to=request.sid)
    else:
        emit('error', {'msg': 'Jogo não encontrado.'}, to=request.sid)

@socketio.on('action_keep_cards')
def handle_keep_cards(data):
    """Recebe a escolha de cartas a manter do jogador Elfo."""
    room = data['room']
    indices = data.get('indices', [])
    game = games.get(room)

    if game:
        success, msg, updated_hands = game.resolve_elfos(request.sid, indices)
        if success:
            if updated_hands:
                for sid, hand in updated_hands.items():
                    emit('private_update', {'hand': hand}, to=sid)
            emit('game_update', game.get_public_state(), room=room)
        else:
            emit('error', {'msg': msg}, to=request.sid)
    else:
        emit('error', {'msg': 'Jogo não encontrado.'}, to=request.sid)

if __name__ == '__main__':
    socketio.run(app, debug=True)