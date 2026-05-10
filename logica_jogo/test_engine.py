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
