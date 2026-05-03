# game_logic/engine.py
from .jogador import Player
from .cartas import generate_deck, REALMS

class EthnosGame:
    def __init__(self, room_id):
        self.room_id = room_id
        self.players = {} # Dicionário de objetos Player
        self.board = {realm: [] for realm in REALMS}
        self.face_up_cards = []
        self.deck = generate_deck()
        self.current_turn = None
        self.dragons_drawn = 0

    def add_player(self, sid, name):
        if len(self.players) < 6:
            self.players[sid] = Player(sid, name)
            if not self.current_turn:
                self.current_turn = sid
            return True
        return False

    def draw_card(self, sid):
        if sid == self.current_turn and len(self.deck) > 0:
            card = self.deck.pop()
            self.players[sid].add_card_to_hand(card)
            self._next_turn()
            return True
        return False

    def _next_turn(self):
        sids = list(self.players.keys())
        current_index = sids.index(self.current_turn)
        self.current_turn = sids[(current_index + 1) % len(sids)]

    def get_public_state(self):
        return {
            'board': self.board,
            'face_up_cards': self.face_up_cards,
            'current_turn': self.players[self.current_turn].name if self.current_turn else None,
            'players': {sid: p.get_public_info() for sid, p in self.players.items()}
        }