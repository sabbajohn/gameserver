from webingo.engines.bingo_math.base import bingo_math_base
import random


INFOS = {"all_extractions": 0,
         "forced_jackpot_extractions": 0,
         "normal_extractions": 0,
         "high_prize_extras_found": 0,
         "high_prize_extras_blocked": 0}

class bigbingo_math( bingo_math_base ):

    def __init__(self, gamedefs, **kwargs):
        super().__init__(gamedefs, **kwargs)
        self.chance_jackpot = kwargs.get("chance_jackpot", 1.0/20000.0)
        self.chance_drop_good_extras = kwargs.get("chance_drop_good_extras", 0.24)
        self.force_next_jackpot = False


    def create_forced_jackpot_extraction( self, series ):

        possible_cards = []

        for i in range(len(series)):
            if series[i]:
                possible_cards.append(i)

        card_idx = random.choice(possible_cards)
        extraction_base: list = super().create_extraction( series )
        naturals = []

        for val in series[card_idx]:
            extraction_base.remove(val)
            naturals.append(val)

        missing = self.naturals - len(naturals)
        naturals += extraction_base[0:missing]
        extras = extraction_base[missing:]

        random.shuffle(naturals)
        random.shuffle(extras)

        return naturals + extras


    def create_extraction( self, series ) :
        """
        extraction logic
        if 1 in 5000: (5000 might come from config)
            force a jackpot :)
        up to 1000 extraction attempts, otherwise use last attempt
        for every generated extraction:
            if extraction is a jackpot: (bingo on naturals)
                discard this extraction
            check the prizes given by extra balls
            if prize is m, w or better:
                (24%, from config) chance to discard the extraction
            accept the extracion, then
        """

        INFOS["all_extractions"] += 1

        if random.random() < self.chance_jackpot or self.force_next_jackpot:
            INFOS["forced_jackpot_extractions"] += 1
            self.force_next_jackpot = False
            return self.create_forced_jackpot_extraction(series)


        INFOS["normal_extractions"] += 1

        base = None
        attempts = 1000
        while attempts:
            base = super().create_extraction(series)
            attempts -= 1

            base_with_extras =  base[:self.naturals+self.extras]
            prizeinfo = self.calc_prizes(base_with_extras, series, 1)
            if prizeinfo["jackpot"]:
                continue

            base_naturals = base[:self.naturals]
            prizeinfo_n = self.calc_prizes(base_naturals, series, 1)

            extra_prizes = bingo_math_base.card_prizes_left_outer_join(prizeinfo["card_prizes"], prizeinfo_n["card_prizes"])
            extras_gives_good_prize = False
            for c in extra_prizes:
                for p in c:
                    prize = self.prizelist[p[0]]
                    if "sbb_blk" in prize and prize["sbb_blk"]:
                        extras_gives_good_prize = True

            if extras_gives_good_prize:
                INFOS["high_prize_extras_found"] += 1
                #logger.debug("\nNATURALS:"+str(prizeinfo_n))
                #logger.debug("WITH_EXTRAS:"+str(prizeinfo))
                bingos = 0
                for c in prizeinfo['card_prizes']:
                    for p in c:
                        if p[0] == 'bingo':
                            bingos += 1
                if bingos == 4:
                    #logger.debug(base_with_extras)
                    #logger.debug(series)
                    pass
                if random.random() < self.chance_drop_good_extras:
                    INFOS["high_prize_extras_blocked"] += 1
                    continue

            # iteration accepted
            return base

        # failsafe
        return base


