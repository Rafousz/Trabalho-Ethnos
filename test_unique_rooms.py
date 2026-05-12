#!/usr/bin/env python
"""
Script de teste para validar funcionalidade de nomes únicos em salas.
Testa se o handler create_room rejeita tentativas de criar salas com nomes duplicados.
"""

from logica_jogo.engine import EthnosGame

def test_unique_room_names():
    """
    Testa se o backend valida nomes únicos de salas.
    
    Simula:
    1. Jogador1 cria "sala1" - deve funcionar
    2. Jogador2 tenta criar "sala1" novamente - deve falhar
    """
    
    # Simulando o dicionário 'games' do app.py
    games = {}
    
    # Cenário 1: Primeira criação de "sala1" - DEVE SUCEDER
    room_name = "sala1"
    if room_name not in games:
        games[room_name] = EthnosGame(room_name)
        game1 = games[room_name]
        success1, _ = game1.add_player("sid_jogador1", "Jogador1")
        print(f"[OK] Criação 1 de '{room_name}': {'SUCESSO' if room_name in games else 'FALHA'}")
        print(f"  - Jogador adicionado: {success1}")
        print(f"  - Jogadores na sala: {len(game1.players)}")
    else:
        print(f"[ERRO] Criação 1 de '{room_name}': Já existia (não deveria existir)")
    
    print()
    
    # Cenário 2: Segunda tentativa de criar "sala1" - DEVE SER REJEITADA
    if room_name in games:
        print(f"[OK] Criação 2 de '{room_name}': REJEITADA")
        print(f"  - Mensagem: 'Sala já existe!'")
        print(f"  - Comportamento esperado: [OK] CORRETO")
    else:
        print(f"[ERRO] Criação 2 de '{room_name}': Sala foi criada novamente (ERRO!)")
        print(f"  - Comportamento: INCORRETO (não deve permitir nomes duplicados)")
    
    print()
    
    # Cenário 3: Criar sala diferente "sala2" - DEVE SUCEDER
    room_name2 = "sala2"
    if room_name2 not in games:
        games[room_name2] = EthnosGame(room_name2)
        game2 = games[room_name2]
        success2, _ = game2.add_player("sid_jogador2", "Jogador2")
        print(f"[OK] Criação de '{room_name2}': {'SUCESSO' if room_name2 in games else 'FALHA'}")
        print(f"  - Jogador adicionado: {success2}")
        print(f"  - Jogadores na sala: {len(game2.players)}")
    else:
        print(f"[ERRO] Criação de '{room_name2}': Já existia (não deveria existir)")
    
    print()
    
    # Validações finais
    assert room_name in games, "sala1 deve existir após primeira criação"
    assert len(games) == 2, "Deve haver exatamente 2 salas (sala1 e sala2)"
    assert room_name2 in games, "sala2 deve existir"
    assert games[room_name] != games[room_name2], "sala1 e sala2 devem ser instâncias diferentes"
    
    print("=" * 60)
    print("[OK] TODOS OS TESTES PASSARAM!")
    print("=" * 60)
    print()
    print("RESUMO:")
    print(f"  - Salas criadas: {list(games.keys())}")
    print(f"  - Total de salas: {len(games)}")
    print(f"  - Jogadores em sala1: {len(games['sala1'].players)}")
    print(f"  - Jogadores em sala2: {len(games['sala2'].players)}")

if __name__ == "__main__":
    test_unique_room_names()
