import random
from .jogador import Player
from .cartas import generate_deck, REALMS

class EthnosGame:
    def __init__(self, room_id):
        self.room_id = room_id
        self.players = {}
        # board agora guarda dicts: {'sid': ..., 'is_troll': bool}
        self.board = {realm: [] for realm in REALMS}
        self.face_up_cards = []
        self.deck = []
        self.current_turn = None
        self.current_era = 1
        self.max_eras = 3
        self.dragons_drawn = 0
        self.game_over = False
        self.winner = None

        # Estado pendente para poderes que precisam de input extra do jogador
        # 'guerreiros': sid aguardando escolha de reino
        # 'elfos': {'sid': ..., 'band_size': ..., 'remaining_cards': [...]}
        self.pending_action = None

        self.available_colors = ['#e74c3c', '#3498db', '#2ecc71', '#f1c40f', '#9b59b6', '#e67e22']
        self.player_colors = {}

        self.glory_tokens = {}
        for realm in REALMS:
            self.glory_tokens[realm] = [
                random.randint(1, 3),
                random.randint(4, 6),
                random.randint(7, 10),
            ]

        self._reset_era_state()

    def _reset_era_state(self):
        self.dragons_drawn = 0
        self.deck = generate_deck()
        self.face_up_cards = []

    def _is_dragon(self, card):
        return bool(card.get('is_dragon'))

    def _draw_until_non_dragon(self):
        if self.game_over:
            return None, False
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
        if not self.players or self.game_over:
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

    def _calcular_pontuacao_era(self):
        for realm, tokens in self.board.items():
            # Contar tokens por sid
            contagem = {}
            troll_sids = set()
            for token in tokens:
                sid = token['sid']
                contagem[sid] = contagem.get(sid, 0) + 1
                if token['is_troll']:
                    troll_sids.add(sid)

            if not contagem:
                continue

            grupos = {}
            for sid, qtd in contagem.items():
                grupos.setdefault(qtd, []).append(sid)

            quantidades_ordenadas = sorted(grupos.keys(), reverse=True)
            pontos_disponiveis = [self.glory_tokens[realm][i] for i in range(self.current_era)]
            pontos_disponiveis.sort(reverse=True)

            posicao_ranking = 0
            for qtd in quantidades_ordenadas:
                jogadores_empatados = grupos[qtd]
                n_empate = len(jogadores_empatados)
                bloco_pontos = pontos_disponiveis[posicao_ranking: posicao_ranking + n_empate]

                if not bloco_pontos:
                    break

                # Poder dos Trolls: desempatar em favor do jogador Troll
                if n_empate > 1:
                    trolls_no_empate = [s for s in jogadores_empatados if s in troll_sids]
                    nao_trolls = [s for s in jogadores_empatados if s not in troll_sids]

                    if len(trolls_no_empate) == 1:
                        # Um único Troll vence o empate: recebe o maior ponto do bloco
                        bloco_ordenado = sorted(bloco_pontos, reverse=True)
                        self.players[trolls_no_empate[0]].score += bloco_ordenado[0]
                        pontos_restantes = bloco_ordenado[1:]
                        if nao_trolls and pontos_restantes:
                            pts_divididos = sum(pontos_restantes) // len(nao_trolls)
                            for s in nao_trolls:
                                self.players[s].score += pts_divididos
                        posicao_ranking += n_empate
                        continue

                # Empate normal: divide igualmente
                total_pontos = sum(bloco_pontos)
                pontos_por_cabeca = total_pontos // n_empate
                for sid in jogadores_empatados:
                    self.players[sid].score += pontos_por_cabeca

                posicao_ranking += n_empate

    def _advance_era(self):
        self._calcular_pontuacao_era()

        if self.current_era < self.max_eras:
            self.current_era += 1
            self._reset_era_state()
            return self._deal_initial_hands()
        else:
            self.game_over = True
            melhor_pontuacao = -1
            vencedores = []
            for p in self.players.values():
                if p.score > melhor_pontuacao:
                    melhor_pontuacao = p.score
                    vencedores = [p.name]
                elif p.score == melhor_pontuacao:
                    vencedores.append(p.name)
            self.winner = " & ".join(vencedores)
            return {}

    def add_player(self, sid, name):
        if len(self.players) >= 6 or self.game_over:
            return False, {}

        self.players[sid] = Player(sid, name)
        if self.available_colors:
            self.player_colors[sid] = self.available_colors.pop(0)
        else:
            self.player_colors[sid] = "#000000"

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
        if self.game_over:
            return False, "O jogo acabou."
        if self.pending_action:
            return False, "Você tem uma ação pendente antes de continuar."
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
        if self.game_over:
            return False, "O jogo acabou."
        if self.pending_action:
            return False, "Você tem uma ação pendente antes de continuar."
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

    def play_band(self, sid, card_indices, realm_alvo=None):
        if self.game_over:
            return False, "O jogo acabou.", None
        if self.pending_action:
            return False, "Você tem uma ação pendente antes de continuar.", None
        if sid != self.current_turn:
            return False, "Não é o seu turno.", None
        if not card_indices:
            return False, "Selecione pelo menos uma carta.", None

        player = self.players[sid]
        hand = player.hand

        if any(i < 0 or i >= len(hand) for i in card_indices):
            return False, "Cartas inválidas selecionadas.", None

        selected_cards = [hand[i] for i in card_indices]
        leader = selected_cards[0]
        leader_tribe = leader['tribe']

        is_valid_tribe = all(c['tribe'] == leader_tribe for c in selected_cards)
        is_valid_realm = all(c['realm'] == leader['realm'] for c in selected_cards)

        if not (is_valid_tribe or is_valid_realm):
            return False, "Bando inválido.", None

        # --- Poder dos Guerreiros: escolha livre de reino ---
        if leader_tribe == 'Guerreiros':
            if realm_alvo is None:
                # Sinaliza ao app que precisa de input do jogador
                self.pending_action = {
                    'type': 'guerreiros_choose_realm',
                    'sid': sid,
                    'card_indices': card_indices,
                }
                return True, 'PENDING_GUERREIROS', None
            if realm_alvo not in REALMS:
                return False, "Reino inválido.", None
        else:
            realm_alvo = leader['realm']

        # --- Poder dos Orcs: bando igual ao número de tokens já basta ---
        if leader_tribe == 'Orcs':
            marcadores_atuais = self._count_tokens(realm_alvo, sid)
            if len(selected_cards) < marcadores_atuais:
                return False, (
                    f"Você não pode jogar este bando. Já tem {marcadores_atuais} "
                    f"token(s) em {realm_alvo} e o bando tem apenas {len(selected_cards)} carta(s)."
                ), None
        else:
            marcadores_atuais = self._count_tokens(realm_alvo, sid)
            if len(selected_cards) <= marcadores_atuais:
                return False, (
                    f"Você não pode jogar este bando. Já tem {marcadores_atuais} "
                    f"token(s) em {realm_alvo} e o bando tem apenas {len(selected_cards)} carta(s)."
                ), None

        # Coloca token no reino (com flag is_troll para desempate)
        is_troll_leader = (leader_tribe == 'Trolls')
        self.board[realm_alvo].append({'sid': sid, 'is_troll': is_troll_leader})

        # Cartas restantes vão para o mercado
        remaining_cards = [c for i, c in enumerate(hand) if i not in card_indices]

        # --- Poder dos Anões: pontos extras pelo tamanho do bando ---
        if leader_tribe == 'Anões':
            player.score += len(selected_cards)

        # --- Poder dos Magos: após descartar, compra N cartas do baralho ---
        if leader_tribe == 'Magos':
            self.face_up_cards.extend(remaining_cards)
            player.hand = []
            n_compras = len(selected_cards)
            for _ in range(n_compras):
                card, era_end = self._draw_until_non_dragon()
                if era_end:
                    updated_hands = self._advance_era()
                    self._next_turn()
                    updated_hands[sid] = list(player.hand)
                    return True, "Bando jogado! Mago comprou cartas e a era avançou.", updated_hands
                if card is None:
                    break
                player.add_card_to_hand(card)
            self._next_turn()
            return True, "Bando jogado com sucesso! (Mago)", {sid: list(player.hand)}

        # --- Poder dos Elfos: mantém N cartas da mão após jogar ---
        if leader_tribe == 'Elfos':
            n_manter = len(selected_cards)
            if remaining_cards and n_manter > 0:
                # Sinaliza que o jogador precisa escolher quais cartas manter
                self.pending_action = {
                    'type': 'elfos_keep_cards',
                    'sid': sid,
                    'n_manter': n_manter,
                    'remaining_cards': remaining_cards,
                }
                player.hand = []
                self._next_turn()
                return True, 'PENDING_ELFOS', {sid: []}
            # Sem cartas restantes, comportamento normal
            self.face_up_cards.extend(remaining_cards)
            player.hand = []
            self._next_turn()
            return True, "Bando jogado com sucesso! (Elfo)", {sid: list(player.hand)}

        # Comportamento padrão: descarta restantes no mercado, esvazia mão
        self.face_up_cards.extend(remaining_cards)
        player.hand = []
        self._next_turn()
        return True, "Bando jogado com sucesso!", {sid: list(player.hand)}

    def resolve_guerreiros(self, sid, realm_alvo):
        """Resolve a escolha de reino pendente do poder dos Guerreiros."""
        if not self.pending_action or self.pending_action.get('type') != 'guerreiros_choose_realm':
            return False, "Nenhuma ação pendente de Guerreiros.", None
        if self.pending_action['sid'] != sid:
            return False, "Não é a sua ação pendente.", None

        card_indices = self.pending_action['card_indices']
        self.pending_action = None

        # Re-executa play_band com o reino escolhido
        return self.play_band(sid, card_indices, realm_alvo=realm_alvo)

    def resolve_elfos(self, sid, indices_manter):
        """Resolve a escolha de cartas a manter do poder dos Elfos."""
        if not self.pending_action or self.pending_action.get('type') != 'elfos_keep_cards':
            return False, "Nenhuma ação pendente de Elfos.", None
        if self.pending_action['sid'] != sid:
            return False, "Não é a sua ação pendente.", None

        n_manter = self.pending_action['n_manter']
        remaining_cards = self.pending_action['remaining_cards']
        self.pending_action = None

        # Valida os índices escolhidos
        indices_manter = list(set(indices_manter))  # remove duplicatas
        if any(i < 0 or i >= len(remaining_cards) for i in indices_manter):
            return False, "Índices inválidos.", None
        if len(indices_manter) > n_manter:
            return False, f"Você pode manter no máximo {n_manter} cartas.", None

        player = self.players[sid]
        cartas_mantidas = [remaining_cards[i] for i in indices_manter]
        cartas_descartadas = [c for i, c in enumerate(remaining_cards) if i not in indices_manter]

        player.hand = cartas_mantidas
        self.face_up_cards.extend(cartas_descartadas)

        return True, "Cartas mantidas com sucesso! (Elfo)", {sid: list(player.hand)}

    def _count_tokens(self, realm, sid):
        """Conta tokens de um sid em um reino (nova estrutura de board)."""
        return sum(1 for t in self.board[realm] if t['sid'] == sid)

    def _next_turn(self):
        if self.game_over:
            return
        sids = list(self.players.keys())
        current_index = sids.index(self.current_turn)
        self.current_turn = sids[(current_index + 1) % len(sids)]

    def get_public_state(self):
        # Converte board para formato simples (lista de sids) para o frontend
        board_public = {
            realm: [t['sid'] for t in tokens]
            for realm, tokens in self.board.items()
        }
        return {
            'board': board_public,
            'glory_tokens': self.glory_tokens,
            'face_up_cards': self.face_up_cards,
            'current_era': self.current_era,
            'max_eras': self.max_eras,
            'dragons_drawn': self.dragons_drawn,
            'game_over': self.game_over,
            'winner': self.winner,
            'pending_action': {
                'type': self.pending_action['type'],
                'sid': self.pending_action['sid'],
            } if self.pending_action else None,
            'current_turn': (
                self.players[self.current_turn].name
                if (self.current_turn and not self.game_over)
                else "Fim de Jogo"
            ),
            'players': {
                sid: {
                    **p.get_public_info(),
                    'color': self.player_colors.get(sid, '#000')
                } for sid, p in self.players.items()
            }
        }