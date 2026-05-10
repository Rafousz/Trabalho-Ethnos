import pytest
from logica_jogo.engine import EthnosGame

def test_hand_limit_draw_card():
    game = EthnosGame('room1')
    game.add_player('sid1', 'Player1')
    game.add_player('sid2', 'Player2')
    
    # Simula o jogador tendo 10 cartas
    player = game.players['sid1']
    player.hand = [{'tribe': 'Centaur', 'realm': 'Stratia', 'is_dragon': False} for _ in range(10)]
    
    # Define de quem é o turno
    game.current_turn = 'sid1'
    
    # Tenta comprar do baralho
    success, msg = game.draw_card('sid1')
    
    assert success is False
    assert msg == "Limite máximo de 10 cartas atingido. Você deve jogar um bando."
    assert len(player.hand) == 10

def test_hand_limit_draw_market_card():
    game = EthnosGame('room1')
    game.add_player('sid1', 'Player1')
    game.add_player('sid2', 'Player2')
    
    player = game.players['sid1']
    player.hand = [{'tribe': 'Centaur', 'realm': 'Stratia', 'is_dragon': False} for _ in range(10)]
    
    game.current_turn = 'sid1'
    game.face_up_cards = [{'tribe': 'Elf', 'realm': 'Pelagia', 'is_dragon': False}]
    
    # Tenta comprar do mercado
    success, msg = game.draw_market_card('sid1', 0)
    
    assert success is False
    assert msg == "Limite máximo de 10 cartas atingido. Você deve jogar um bando."
    assert len(player.hand) == 10
