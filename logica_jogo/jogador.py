class Player:
    def __init__(self, sid, name):
        self.sid = sid
        self.name = name
        self.hand = []
        self.score = 0
        self.tokens_placed = 0

    def add_card_to_hand(self, card):
        self.hand.append(card)

    def get_public_info(self):
        # Oculta as cartas da mão, mostrando apenas a quantidade
        return {
            'name': self.name,
            'hand_size': len(self.hand),
            'score': self.score
        }