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
    
    success, result = game.draw_card('sid1')
    
    assert success is False
    assert result == "Limite máximo de 10 cartas atingido. Você deve jogar um bando."
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
    
    success, result = game.draw_market_card('sid1', 0)
    
    assert success is False
    assert result == "Limite máximo de 10 cartas atingido. Você deve jogar um bando."
    assert len(player.hand) == 10

def test_play_band_with_equal_cards_and_tokens():
    """Testa se bando com cartas == tokens é recusado."""
    game = EthnosGame('room1')
    game.add_player('sid1', 'Player1')
    game.add_player('sid2', 'Player2')
    
    player = game.players['sid1']
    player.hand = [
        {'tribe': 'Guerreiros', 'realm': 'strath', 'is_dragon': False},
        {'tribe': 'Guerreiros', 'realm': 'strath', 'is_dragon': False}
    ]
    
    # Coloca 2 tokens do jogador em strath (nova estrutura de board)
    game.board['strath'] = [
        {'sid': 'sid1', 'is_troll': False},
        {'sid': 'sid1', 'is_troll': False}
    ]
    game.current_turn = 'sid1'
    
    # Guerreiros com 2 cartas == 2 tokens: ainda deve ser recusado (Guerreiros só muda o reino, não a regra de quantidade)
    # Para testar a regra de quantidade sem interferência do poder, usamos outra tribo
    player.hand = [
        {'tribe': 'Magos', 'realm': 'strath', 'is_dragon': False},
        {'tribe': 'Magos', 'realm': 'strath', 'is_dragon': False}
    ]
    
    success, msg, _ = game.play_band('sid1', [0, 1])
    
    assert success is False
    assert "Você não pode jogar este bando" in msg
    assert len(player.hand) == 2
    assert len(game.board['strath']) == 2

def test_play_band_with_fewer_cards_than_tokens():
    """Testa se bando com cartas < tokens é recusado."""
    game = EthnosGame('room1')
    game.add_player('sid1', 'Player1')
    game.add_player('sid2', 'Player2')
    
    player = game.players['sid1']
    player.hand = [
        {'tribe': 'Magos', 'realm': 'pelia', 'is_dragon': False}
    ]
    
    # Coloca 3 tokens do jogador em pelia (nova estrutura de board)
    game.board['pelia'] = [
        {'sid': 'sid1', 'is_troll': False},
        {'sid': 'sid1', 'is_troll': False},
        {'sid': 'sid1', 'is_troll': False}
    ]
    game.current_turn = 'sid1'
    
    success, msg, _ = game.play_band('sid1', [0])
    
    assert success is False
    assert "Você não pode jogar este bando" in msg
    assert len(player.hand) == 1
    assert len(game.board['pelia']) == 3

def test_play_band_with_more_cards_than_tokens():
    """Testa se bando com cartas > tokens é aceito."""
    game = EthnosGame('room1')
    game.add_player('sid1', 'Player1')
    game.add_player('sid2', 'Player2')
    
    player = game.players['sid1']
    # Trolls: poder de desempate na pontuação, comportamento de mão padrão (esvazia)
    player.hand = [
        {'tribe': 'Trolls', 'realm': 'nida', 'is_dragon': False},
        {'tribe': 'Trolls', 'realm': 'nida', 'is_dragon': False},
        {'tribe': 'Trolls', 'realm': 'pelia', 'is_dragon': False}  # Carta que vai pro mercado
    ]
    
    # Coloca 1 token do jogador em nida (nova estrutura de board)
    game.board['nida'] = [{'sid': 'sid1', 'is_troll': False}]
    game.current_turn = 'sid1'
    
    success, msg, _ = game.play_band('sid1', [0, 1])
    
    assert success is True
    assert len(player.hand) == 0
    assert len(game.board['nida']) == 2  # Um novo token foi adicionado
    assert len(game.face_up_cards) == 1  # A carta restante foi pro mercado

def test_trolls_tiebreak_in_era_scoring():
    """Testa se o Troll vence o empate na pontuação da era."""
    game = EthnosGame('room1')
    game.add_player('sid_troll', 'Troll Player')
    game.add_player('sid_normal', 'Normal Player')
    game.player_colors['sid_troll'] = '#9b59b6'
    game.player_colors['sid_normal'] = '#2ecc71'

    # Define pontos conhecidos: era 1 = 4pts, era 2 = 7pts
    game.glory_tokens['strath'] = [4, 7, 10]
    game.current_era = 2

    # Empate: 1 token cada, mas sid_troll tem is_troll=True
    game.board['strath'] = [
        {'sid': 'sid_troll', 'is_troll': True},
        {'sid': 'sid_normal', 'is_troll': False},
    ]

    game._calcular_pontuacao_era()

    # Com 2 eras, pontos disponíveis são [4, 7] → ordenados desc: [7, 4]
    # Troll desempata: recebe 7, normal recebe 4
    assert game.players['sid_troll'].score == 7
    assert game.players['sid_normal'].score == 4

def test_elfos_keeps_chosen_cards_after_band():
    """Testa se o Elfo mantém as cartas escolhidas e descarta o resto para o mercado."""
    game = EthnosGame('room1')
    game.add_player('sid1', 'Player1')
    game.add_player('sid2', 'Player2')

    player = game.players['sid1']
    carta_manter  = {'tribe': 'Guerreiros', 'realm': 'fara',   'is_dragon': False}
    carta_descartar = {'tribe': 'Magos',     'realm': 'shetan', 'is_dragon': False}

    # Bando de 2 Elfos + 2 cartas restantes (pode manter até 2)
    player.hand = [
        {'tribe': 'Elfos', 'realm': 'alara', 'is_dragon': False},
        {'tribe': 'Elfos', 'realm': 'pelia', 'is_dragon': False},
        carta_manter,
        carta_descartar,
    ]
    game.board['alara'] = []
    game.current_turn = 'sid1'

    # Joga bando de Elfos (índices 0 e 1) — dispara PENDING_ELFOS
    success, msg, _ = game.play_band('sid1', [0, 1])
    assert success is True
    assert msg == 'PENDING_ELFOS'

    # Resolve mantendo só carta_manter (índice 0 das restantes) e descartando carta_descartar
    success2, msg2, updated = game.resolve_elfos('sid1', [0])
    assert success2 is True
    assert player.hand == [carta_manter]           # só a carta escolhida ficou na mão
    assert carta_descartar in game.face_up_cards   # a descartada foi ao mercado

def test_anoes_score_bonus_equals_band_size():
    """Testa se os Anões recebem pontos extras iguais ao tamanho do bando jogado."""
    game = EthnosGame('room1')
    game.add_player('sid1', 'Player1')
    game.add_player('sid2', 'Player2')

    player = game.players['sid1']
    player.hand = [
        {'tribe': 'Anões', 'realm': 'nida', 'is_dragon': False},
        {'tribe': 'Anões', 'realm': 'fara', 'is_dragon': False},
        {'tribe': 'Anões', 'realm': 'pelia', 'is_dragon': False},
    ]
    game.board['nida'] = []
    game.current_turn = 'sid1'

    score_antes = player.score
    success, msg, _ = game.play_band('sid1', [0, 1, 2])

    assert success is True
    assert player.score == score_antes + 3  # bando de 3 cartas → +3 pontos