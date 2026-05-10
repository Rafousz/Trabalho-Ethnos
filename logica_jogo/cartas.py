# game_logic/cards.py
import random

TRIBES = ['Guerreiros', 'Elfos', 'Anões', 'Orcs', 'Magos', 'Trolls']
REALMS = ['strath', 'pelia', 'nida', 'shetan', 'alara', 'fara']
DRAGON_TRIBE = 'Dragao'
DRAGON_REALM = 'Especial'
DRAGON_COUNT = 3

def generate_deck():
    # Cria o baralho base combinando tribos e reinos
    deck = [
        {'tribe': t, 'realm': r, 'is_dragon': False}
        for t in TRIBES
        for r in REALMS
    ]
    deck.extend(
        {
            'tribe': DRAGON_TRIBE,
            'realm': DRAGON_REALM,
            'is_dragon': True,
        }
        for _ in range(DRAGON_COUNT)
    )
    random.shuffle(deck)
    return deck