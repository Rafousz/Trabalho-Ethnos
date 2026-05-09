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

    def draw_market_card(self, sid, card_index):
        if sid == self.current_turn and 0 <= card_index < len(self.face_up_cards):
            card = self.face_up_cards.pop(card_index)
            self.players[sid].add_card_to_hand(card)
            self._next_turn()
            return True
        return False

    def play_band(self, sid, card_indices):
        if sid != self.current_turn:
            return False, "Não é o seu turno."
        if not card_indices:
            return False, "Selecione pelo menos uma carta."
            
        player = self.players[sid]
        hand = player.hand
        
        # Validar índices
        if any(i < 0 or i >= len(hand) for i in card_indices):
            return False, "Cartas inválidas selecionadas."
            
        selected_cards = [hand[i] for i in card_indices]
        leader = selected_cards[0]
        
        # Verificar se é um bando válido (mesma tribo ou mesmo reino)
        is_valid_tribe = all(c['tribe'] == leader['tribe'] for c in selected_cards)
        is_valid_realm = all(c['realm'] == leader['realm'] for c in selected_cards)
        
        if not (is_valid_tribe or is_valid_realm):
            return False, "Bando inválido. As cartas devem ter a mesma tribo ou o mesmo reino."
            
        # O descarte: remover as cartas jogadas da mão
        remaining_cards = [c for i, c in enumerate(hand) if i not in card_indices]
        
        # Todas as cartas que sobraram na mão vão para o mercado (mesa)
        self.face_up_cards.extend(remaining_cards)
        
        # A mão do jogador fica vazia
        player.hand = []
        
        # Passa o turno
        self._next_turn()
        return True, "Bando jogado com sucesso!"

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