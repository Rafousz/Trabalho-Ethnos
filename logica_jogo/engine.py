# game_logic/engine.py
from .jogador import Player
from .cartas import generate_deck, REALMS

class EthnosGame:
    def __init__(self, room_id):
        self.room_id = room_id
        self.players = {} # Dicionário de objetos Player
        self.board = {realm: [] for realm in REALMS}
        self.face_up_cards = []
        self.deck = []
        self.current_turn = None
        self.current_era = 1
        self.max_eras = 3
        self.dragons_drawn = 0
        self._reset_era_state()

    def _reset_era_state(self):
        self.dragons_drawn = 0
        self.deck = generate_deck()
        self.face_up_cards = []

    def _is_dragon(self, card):
        return bool(card.get('is_dragon'))

    def _draw_until_non_dragon(self):
        while self.deck:
            card = self.deck.pop()
            if self._is_dragon(card):
                self.face_up_cards.append(card)
                self.dragons_drawn += 1
                if self.dragons_drawn >= 3:
                    return None, True
                continue
            return card, False
        return None, False

    def _deal_initial_hands(self):
        updated_hands = {}
        if not self.players:
            return updated_hands

        for player in self.players.values():
            player.hand = []

        for sid, player in self.players.items():
            card, era_end = self._draw_until_non_dragon()
            if era_end:
                return self._advance_era()
            if card is None:
                return updated_hands
            player.add_card_to_hand(card)
            updated_hands[sid] = list(player.hand)

        return updated_hands

    def _advance_era(self):
        self.current_era += 1
        self._reset_era_state()
        return self._deal_initial_hands()

    def add_player(self, sid, name):
        if len(self.players) >= 6:
            return False, {}

        self.players[sid] = Player(sid, name)
        if not self.current_turn:
            self.current_turn = sid

        updated_hands = {}
        card, era_end = self._draw_until_non_dragon()
        if era_end:
            updated_hands = self._advance_era()
        elif card is not None:
            self.players[sid].add_card_to_hand(card)
            updated_hands[sid] = list(self.players[sid].hand)

        return True, updated_hands

    def draw_card(self, sid):
        if sid != self.current_turn:
            return False, "Não é o seu turno."
            
        if len(self.players[sid].hand) >= 10:
            return False, "Limite máximo de 10 cartas atingido. Você deve jogar um bando."

        card, era_end = self._draw_until_non_dragon()
        if era_end:
            updated_hands = self._advance_era()
            self._next_turn()
            return True, updated_hands

        if card is None:
            return False, "O baralho está vazio."

        self.players[sid].add_card_to_hand(card)
        self._next_turn()
        return True, {sid: list(self.players[sid].hand)}

    def draw_market_card(self, sid, card_index):
        if sid != self.current_turn:
            return False, "Não é o seu turno."
            
        if len(self.players[sid].hand) >= 10:
            return False, "Limite máximo de 10 cartas atingido. Você deve jogar um bando."

        if 0 <= card_index < len(self.face_up_cards):
            card = self.face_up_cards[card_index]
            if self._is_dragon(card):
                return False, "Não é possível comprar um dragão."
            card = self.face_up_cards.pop(card_index)
            self.players[sid].add_card_to_hand(card)
            self._next_turn()
            return True, {sid: list(self.players[sid].hand)}
        return False, "Carta inválida."

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
            'current_era': self.current_era,
            'max_eras': self.max_eras,
            'dragons_drawn': self.dragons_drawn,
            'current_turn': self.players[self.current_turn].name if self.current_turn else None,
            'players': {sid: p.get_public_info() for sid, p in self.players.items()}
        }