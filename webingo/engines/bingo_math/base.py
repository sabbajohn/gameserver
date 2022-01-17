import copy
import random

from abc import ABC
from webingo.support import logger
from .utils import randi

DEFAULT_NATURALS = 30
DEFAULT_EXTRAS = 11
DEFAULT_MAX_CARDS = 4
DEFAULT_BALL_COUNT = 60
AGGRESSIVE_PRINTS = False


class bingo_math_base(ABC):

    def __init__(self, gamedefs, **kwargs ):
        self.naturals = int(kwargs["naturals"]) if "naturals" in kwargs else DEFAULT_NATURALS
        self.extras = int(kwargs["extras"]) if "extras" in kwargs else DEFAULT_EXTRAS
        self.max_cards = int(kwargs["max_cards"]) if "max_cards" in kwargs else DEFAULT_MAX_CARDS
        self.ball_count = int(kwargs["ball_count"]) if "ball_count" in kwargs else DEFAULT_BALL_COUNT

        # won't make this parameterizable for now
        self.card_size = 15

        self.gamedefs = gamedefs
        self.prizelist = gamedefs["prizes"]
        self._calc_prize_overrides()

        # TODO get game currency information somehow? (get "CRE")
        self.min_bet = self.gamedefs["betcontrol"]["CRE"]["min_bet"]

    def create_series(self, num_cards=-1):

        if num_cards <= 0:
            num_cards = self.max_cards

        lst = list(range(1, 1 + 60))
        random.shuffle(lst)

        cards = []
        cs = self.card_size
        for i in range(num_cards):
            cards.append(lst[i*cs:(i+1)*cs])

        if self.card_size == 15:
            sorted_cards = []
            for card in cards:
                card.sort()
                card_by_column = []
                for l in range(3):
                    for c in range(5):
                        card_by_column.append( card[c*3 + l] )
                sorted_cards.append(card_by_column)
            return sorted_cards

        logger.error("[bingo_math_base] DON'T KNOW HOW TO SORT CARDS DIFFERENT FROM SIZE 15, FIXME")
        return cards


    # override this for more complex rules in allowing some extractions and not allowing others
    # FIXME: use series parameters
    def create_extraction( self, series ):
        l = list(range(1, 1 + 60))
        random.shuffle(l)
        return l


    def create_forced_prize_extraction(self, series, prize_name):
        possible_cards = []

        exchange_first_extra = prize_name == "bingo"
        if prize_name == "Jackpot":
            prize_name = "bingo"

        for i in range(len(series)):
            if series[i]:
                possible_cards.append(i)

        card_idx = random.choice(possible_cards)
        extraction_base: list = self.create_extraction( series )
        naturals = []
        ignores = []

        pattern = random.choice(self.prizelist[prize_name]["patterns"])

        for i in range(len(series[card_idx])):
            val = series[card_idx][i]
            if pattern[i]:
                extraction_base.remove(val)
                naturals.append(val)
            else:
                ignores.append(val)

        # move ignore list balls to end of extraction
        extraction_base = list(filter(lambda x: x not in ignores, extraction_base))
        extraction_base = extraction_base + ignores

        # complete extraction
        missing = self.naturals - len(naturals)
        naturals += extraction_base[0:missing]
        extras = extraction_base[missing:]

        inbetween = []
        if exchange_first_extra:
            inbetween = [naturals[0]]
            naturals[0] = extras[0]
            extras = extras[1:]

        random.shuffle(naturals)
        random.shuffle(extras)

        ret = naturals + inbetween + extras

        return ret

    def check_free_slot(self, prize_pattern, positions):
        for position in range(len(prize_pattern)):
            if prize_pattern[position] == 1:
                if positions[position]:
                    return True
        return False

    def take_slot(self, prize_pattern, free_positions):
        positions = free_positions
        for position in range(len(prize_pattern)):
            if prize_pattern[position] == 1:
                positions[position] = False
        return positions

    # it's a bad idea to override this, but some behaviors could be put into the interface, maybe
    def calc_prizes(self, allballs, cards, bet_per_card):
        ret = {}

        prizelist = self.prizelist
        naturals = copy.copy(allballs)[:self.naturals]
        jackpot_cards = []
        cardmasks = []
        card_idx = 0
        for card in cards:
            natural_count = 0
            mask = []
            cardmasks.append(mask)
            for i in range(self.card_size):
                if card[i] in allballs:
                    mask.append(1)
                else:
                    mask.append(0)
                if card[i] in naturals:
                    natural_count += 1
            if natural_count == self.card_size:
                jackpot_cards.append(card_idx)
            card_idx += 1

        if AGGRESSIVE_PRINTS:
            logger.debug("CARDMASKS:" + str(cardmasks))

        hasPifado = False
        hasBonus = False

        cardWinnings = [0] * len(cards)
        cardPifados  = [0] * len(cards)
        cardPifadosRaw  = [0] * len(cards)
        cardPifadoBingo = [False] * len(cards)
        cardIndexPifadoBingo = -1
        cardPrizes =  []

        # TODO: Today we get prizes' ordination directly from manifest.json
        # file, transform it to ordenate through payment
        prizes_list_name = [u for u in prizelist.keys()]
        prizes_list_name.reverse()
        for i in range(len(cards)):
            cardPrizes.append([])

        for i in range(len(cards)):            # for every bingo card
            free_positions = [True] * 15
            overlapping_prizes = []
            for prizename in prizes_list_name:           # for every prize
                prize = prizelist[prizename]
                # for every prize on the list, see if this card matches its pattern
                for pattern_idx in range(len(prize["patterns"])):
                    pattern = prize["patterns"][pattern_idx]
                    notMatching = 0
                    for j in range(15): # this for
                        if pattern[j]:
                            if not cardmasks[i][j]:
                                notMatching += 1
                                if notMatching > 1:
                                    break # that for
                    if notMatching == 0:
                        # found a match
                        if self.check_free_slot(pattern, free_positions):
                            free_positions = self.take_slot(pattern,
                                                            free_positions)
                            overlapping_prizes.append((prizename, pattern_idx))
                    elif notMatching == 1 and prize["pifa"]:
                        hasPifado = True
                        if AGGRESSIVE_PRINTS:
                            logger.debug(prizename + " PIFADO in card " + str(i) )
                        cardPifadosRaw[i] += int(prize["pays"])
                        cardPifados[i] += int(prize["pays"]) * bet_per_card
                        if prizename == "bingo":
                            cardPifadoBingo[i] = True
                            cardIndexPifadoBingo = i
                    elif notMatching == 1:
                        cardPifadosRaw[i] += int(prize["pays"])
                        cardPifados[i] += int(prize["pays"]) * bet_per_card

            if AGGRESSIVE_PRINTS:
                logger.debug(f"OVERLAPPING in card {i}: " + str(overlapping_prizes))

            # Now we collect all the prizes' names of this card and put it on
            # a list.
            final_prizes = [i[0] for i in overlapping_prizes]
            # we have the final list of prizes for this card
            # let's check other details
            for prize in final_prizes:
                if prizelist[prize]["bonus"]:
                    hasBonus = True
                if AGGRESSIVE_PRINTS:
                    logger.debug(prize + " in card " + str(i))
                prize_won = int(prizelist[prize]["pays"]) * bet_per_card
                cardPrizes[i].append((prize, prize_won))
                cardWinnings[i] += prize_won

        ret["has_extra"] = hasPifado or len(allballs) > self.naturals
        ret["has_bonus"] = hasBonus
        ret["card_wins"] = cardWinnings
        ret["jackpot"] = bool(jackpot_cards)
        ret["jackpot_cards"] = jackpot_cards
        ret["card_prizes"] = cardPrizes
        ret["card_pifados"] = cardPifados
        ret["card_pifados_raw"] = cardPifadosRaw
        ret["card_index_pifado_bingo"] = cardIndexPifadoBingo
        ret["bet_per_card"] = bet_per_card
        ret["extra_ball_count"] = len(allballs) - self.naturals

        return ret



    # translated from prizes.gd in joker_bingo on 2020-06-13
    # calcula_preco_be
    def calc_extra_ball_price(self, prize_info):
        soma_premios = sum(prize_info["card_pifados_raw"])
        porcentagem_be = [ 0.035, 0.035, 0.035, 0.035, 0.035, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04 ]
        # discount = 0.001 # -> 96 teorico, 89 real
        # discount = 0.009 # -> 96,48 teorico, 105 real
        # discount = 0.006 # -> 88,62 teorico
        # discount = 0.007 # -> 91,41 teorico, real 95,9, antes fix sobrepos
        # discount = 0.007 # -> 84,40 teorico, real ??,?, depois fix sobrepos
        # discount = 0.0104# -> 94,60 teorico, real 103
        discount = 0.01    # -> 91,99 teorico

        bet_real = prize_info["bet_per_card"]
        soma_premios *= bet_real

        extra_index = prize_info["extra_ball_count"]
        if extra_index >= self.extras or extra_index < 0 or extra_index >= len(porcentagem_be):
            return bet_real

        cartela_pifada_bingo = prize_info["card_index_pifado_bingo"]
        if cartela_pifada_bingo >= 0:
            valor_bingo = self.prizelist['bingo']['pays'] * bet_real
            valor_premio_cartela = prize_info["card_wins"][cartela_pifada_bingo]  # FIXME: tem que retornar o que ja ganhou, nao o que vai ganhar
            if valor_premio_cartela >= int(valor_bingo / 3):  # se ja ganhou mais de 1/3 do bingo, cobra menos pela BE
                soma_premios = valor_bingo - valor_premio_cartela

        valor_calculado = soma_premios * (porcentagem_be[extra_index] - discount)

        variacao_porcentagem = random.random() * (0.05 if soma_premios >= 500 else 0.10)

        valor_calculado *= (1 + variacao_porcentagem * random.choice([1, -1]))

        if valor_calculado < 1:
            valor_calculado = 1

        # 1 em 5: extra gratis
        if valor_calculado <= bet_real:
            if randi(1000) < 200:
                valor_calculado = 0

        preco_final = int(valor_calculado)

        return preco_final


    # prize calculation depends on this, careful when overriding
    def _calc_prize_overrides(self):

        prizelist = self.prizelist

        for superior in prizelist:
            sup_over = []

            for inferior in prizelist:
                if superior == inferior:
                    continue
                sup_obj = prizelist[superior]
                inf_obj = prizelist[inferior]

                # ensure the superior is a higher-paying prize
                if inf_obj['pays'] > sup_obj['pays']:
                    continue

                for s_pat in sup_obj['patterns']:
                    s_pat_idx = sup_obj['patterns'].index(s_pat)
                    for i_pat in inf_obj['patterns']:
                        i_pat_idx = inf_obj['patterns'].index(i_pat)
                        found_hole = False
                        for i in range(15):
                            if(i_pat[i] and not s_pat[i]):
                                found_hole = True
                                break
                        if not found_hole:
                            sup_over.append((s_pat_idx, inferior, i_pat_idx))

            sup_obj['overrides'] = sup_over
            if AGGRESSIVE_PRINTS:
                logger.debug("SUPERIOR_OVERRIDES:" + str(sup_over))
            for o in sup_over:
                if AGGRESSIVE_PRINTS:
                    logger.debug("{}({}) overrides {}({})".format(superior, o[0], o[1], o[2]))


    @staticmethod
    def card_prizes_left_outer_join( left_cp, right_cp ):
        outer_prizes = []

        for c_idx in range(len(left_cp)):

            outer_prizes.append([])

            c_left = left_cp[c_idx]
            c_right = right_cp[c_idx]

            for p in c_left:
                if p not in c_right:
                    outer_prizes[-1].append(p)

        return outer_prizes
