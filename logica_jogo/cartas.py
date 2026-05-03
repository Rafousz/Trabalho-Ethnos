# game_logic/cards.py
import random

TRIBES = ['Centauros', 'Elfos', 'Anões', 'Orcs', 'Magos', 'Trolls']
REALMS = ['strath', 'pelia', 'nida', 'shetan', 'alara', 'fara']

def generate_deck():
    # Cria o baralho base combinando tribos e reinos
    deck = [{'tribe': t, 'realm': r} for t in TRIBES for r in REALMS]
    random.shuffle(deck)
    return deck