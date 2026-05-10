import pytest
from logica_jogo.engine import EthnosGame

def test_initialization():
    """Testa se o jogo inicia com o estado correto."""
    game = EthnosGame("sala_teste")
    assert game.room_id == "sala_teste"
    assert game.current_era == 1
    assert len(game.players) == 0
    assert game.dragons_drawn == 0

def test_add_player():
    """Testa a adição de um jogador."""
    game = EthnosGame("sala_teste")
    success, hands = game.add_player("sid_123", "Jogador 1")
    
    assert success is True
    assert "sid_123" in game.players
    assert game.players["sid_123"].name == "Jogador 1"
    assert game.current_turn == "sid_123"
    
    # O jogador deve receber 1 carta inicial que não é dragão
    assert len(game.players["sid_123"].hand) == 1
    assert not game.players["sid_123"].hand[0].get('is_dragon')

def test_max_players():
    """Testa o limite máximo de 6 jogadores."""
    game = EthnosGame("sala_teste")
    
    # Adiciona 6 jogadores
    for i in range(6):
        success, _ = game.add_player(f"sid_{i}", f"Jogador {i}")
        assert success is True
        
    # Tenta adicionar o 7º jogador
    success, _ = game.add_player("sid_6", "Jogador Extra")
    assert success is False
    assert len(game.players) == 6

def test_deck_generation():
    """Testa se o baralho é gerado com a quantidade correta de cartas e dragões."""
    game = EthnosGame("sala_teste")
    deck = game.deck
    
    # 6 tribos x 6 reinos = 36 cartas normais + 3 dragões = 39 cartas no total
    assert len(deck) == 39
    
    dragons = [card for card in deck if card.get('is_dragon')]
    assert len(dragons) == 3

def test_hand_limit_draw_card():
    """Testa se o limite de 10 cartas impede a compra do baralho."""
    game = EthnosGame('room1')
    game.add_player('sid1', 'Player1')
    game.add_player('sid2', 'Player2')
    
    player = game.players['sid1']
    player.hand = [{'tribe': 'Centaur', 'realm': 'Stratia', 'is_dragon': False} for _ in range(10)]
    
    game.current_turn = 'sid1'
    
    success, msg = game.draw_card('sid1')
    
    assert success is False
    assert msg == "Limite máximo de 10 cartas atingido. Você deve jogar um bando."
    assert len(player.hand) == 10

def test_hand_limit_draw_market_card():
    """Testa se o limite de 10 cartas impede a compra do mercado."""
    game = EthnosGame('room1')
    game.add_player('sid1', 'Player1')
    game.add_player('sid2', 'Player2')
    
    player = game.players['sid1']
    player.hand = [{'tribe': 'Centaur', 'realm': 'Stratia', 'is_dragon': False} for _ in range(10)]
    
    game.current_turn = 'sid1'
    game.face_up_cards = [{'tribe': 'Elf', 'realm': 'Pelagia', 'is_dragon': False}]
    
    success, msg = game.draw_market_card('sid1', 0)
    
    assert success is False
    assert msg == "Limite máximo de 10 cartas atingido. Você deve jogar um bando."
    assert len(player.hand) == 10

def test_play_band_with_equal_cards_and_tokens():
    """Testa se bando com cartas == tokens é recusado."""
    game = EthnosGame('room1')
    game.add_player('sid1', 'Player1')
    game.add_player('sid2', 'Player2')
    
    player = game.players['sid1']
    # Prepara mão com 2 cartas do mesmo reino
    player.hand = [
        {'tribe': 'Centaur', 'realm': 'Stratia', 'is_dragon': False},
        {'tribe': 'Centaur', 'realm': 'Stratia', 'is_dragon': False}
    ]
    
    # Coloca 2 tokens do jogador em Stratia
    game.board['Stratia'] = ['sid1', 'sid1']
    game.current_turn = 'sid1'
    
    # Tenta jogar bando com 2 cartas (mesmo número de tokens)
    success, msg = game.play_band('sid1', [0, 1])
    
    assert success is False
    assert "Você não pode jogar este bando" in msg
    assert len(player.hand) == 2  # Cartas não foram descartadas
    assert len(game.board['Stratia']) == 2  # Nenhum token novo foi adicionado

def test_play_band_with_fewer_cards_than_tokens():
    """Testa se bando com cartas < tokens é recusado."""
    game = EthnosGame('room1')
    game.add_player('sid1', 'Player1')
    game.add_player('sid2', 'Player2')
    
    player = game.players['sid1']
    # Prepara mão com 1 carta
    player.hand = [
        {'tribe': 'Centaur', 'realm': 'Stratia', 'is_dragon': False}
    ]
    
    # Coloca 3 tokens do jogador em Stratia
    game.board['Stratia'] = ['sid1', 'sid1', 'sid1']
    game.current_turn = 'sid1'
    
    # Tenta jogar bando com 1 carta (menos que 3 tokens)
    success, msg = game.play_band('sid1', [0])
    
    assert success is False
    assert "Você não pode jogar este bando" in msg
    assert len(player.hand) == 1  # Carta não foi descartada
    assert len(game.board['Stratia']) == 3  # Nenhum token novo foi adicionado

def test_play_band_with_more_cards_than_tokens():
    """Testa se bando com cartas > tokens é aceito."""
    game = EthnosGame('room1')
    game.add_player('sid1', 'Player1')
    game.add_player('sid2', 'Player2')
    
    player = game.players['sid1']
    # Prepara mão com 3 cartas (2 do mesmo reino e 1 diferente que irá pro mercado)
    player.hand = [
        {'tribe': 'Centaur', 'realm': 'Stratia', 'is_dragon': False},
        {'tribe': 'Centaur', 'realm': 'Stratia', 'is_dragon': False},
        {'tribe': 'Elf', 'realm': 'Pelagia', 'is_dragon': False}  # Carta que vai pro mercado
    ]
    
    # Coloca 1 token do jogador em Stratia
    game.board['Stratia'] = ['sid1']
    game.current_turn = 'sid1'
    
    # Joga bando com 2 cartas de Stratia (mais que 1 token)
    success, msg = game.play_band('sid1', [0, 1])
    
    assert success is True
    assert len(player.hand) == 0  # Todas as cartas foram descartadas
    assert len(game.board['Stratia']) == 2  # Um novo token foi adicionado
    assert len(game.face_up_cards) == 1  # A carta restante foi pro mercado

