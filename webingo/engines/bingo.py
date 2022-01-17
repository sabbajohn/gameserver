from .base import GameEngine
from webingo.support import logger
import random, copy
import webingo.transaction.round as rounds
import webingo.transaction.outlet as round_outlet
from webingo.transaction.outlet_new import OutletNew
from webingo.engines.bingo_math.factory import create_bingo_math

NUM_NORMAL_BALLS = 30
NUM_EXTRA_BALLS = 11

AGGRESSIVE_PRINTS = False


class BingoEngine(GameEngine):
    
    def __init__(self, game, session_registry, wallet, round_process_callback=None):
        GameEngine.__init__(self)
        self.wallet = wallet
        self.session_registry = session_registry
        self.rgs_session = session_registry.get_session_id()
        self.curr_round: rounds.round = None
        self.round_process_callback = None

        self.game = game
        self.gamedefs = game.gamedefs
        self.parse_gamedefs()
        self.target_pot = None
        
        self.idle_state_setup()
        self.internal_state = {}
        self.total_natural_wins = 0
        self.lobby_version = None
        self.game_version = None
    def parse_gamedefs(self):
        self.gamedefs = copy.copy( self.gamedefs )
        self.math = create_bingo_math("bigbingo", self.gamedefs, **{})  # TODO get math id and configuration from gamedefs
        self.prizes = self.math.prizelist


    def idle_state_setup(self, change_cards = False):
        prev_cards = self.state['data']['cards'] if (hasattr(self, 'state') and 'data' in self.state and 'cards' in self.state['data']) else None
        state_data = {
            'cards': prev_cards if (prev_cards and not change_cards) else self.math.create_series(),
            'balls': [],
            'extraballs':[]
        }
        
        self.state = {
            'id': self.gen_state_id(),
            'name': 'idle',
            'data': state_data,
            'actions': ['bet', 'cards']
        }
    
    def type(self):
        return "bingo"

    def get_state(self):
        return self.state
    def do_action(self, action, args, stateid):
        
        if self.state['id'] != stateid:
            logger.warning("[bingo] action state id mismatch")
            return

        if action != "test_prize" and action not in self.state['actions']:
            logger.warning("[bingo] action '"+action+"'not valid in current state: " + self.state['name'])
            return
        
        if self.state['name'] == 'idle':
            if action == 'bet':
                self.bet(args)
            elif action == 'test_prize':
                if 'amount' not in args:
                    args['amount'] = 50
                self.bet(args, True)
            elif action == 'cards':
                self.idle_state_setup(True)
        elif self.state['name'] == 'game':
            if action == 'end':
                self.end_play()
                self.idle_state_setup()
            elif action == 'bet':
                self.end_play()
                self.idle_state_setup()
            elif action == 'cards':
                self.end_play()
                self.idle_state_setup(True)
            elif action == 'test_prize':
                if 'amount' not in args:
                    args['amount'] = 50
                self.end_play()
                self.idle_state_setup()
                self.bet(args, True)
            elif action == 'extra':
                self.buy_extra_ball()

    def bet(self, bet_args, test_prize=False):
        if self.state['data']['balls']:
            logger.error("[bingoengine] we already have balls in the game, bet already done")
            return

        if self.curr_round:
            logger.error("[bingoengine] a round is currently in progress, can't bet")
            return

        bet_amount = int(bet_args['amount'])
        creds = self.wallet.combined_credits()
        if( creds < bet_amount ):
            return # we already have balls in the game, bet already done

        if( bet_amount % 4 ):
            logger.error("[bingoengine] FIXME: betting on four cards is hardcoded for now")
            return

        # not manipulating wallet directly anymore, everything goes via round
        # self.wallet.charge_credits( bet_amount )

        self.state['data']['bet'] = bet_amount
        rgs_game_id_int = rounds.round.get_game_rgs_int(self.game.name, self.session_registry)
        self.curr_round = rounds.round(rgs_game_id_int, self.wallet, False, { "engine": "bingo", "engine_version": 1 })
        tx = rounds.build_transaction(rounds.round.TYPE_BET, "bet", bet_amount, "", {})
        self.curr_round.add_transaction(tx)
        self.state['data']['round_id'] = self.curr_round.unique_id

        l = self.math.create_extraction( self.state['data']['cards'] )\
            if not test_prize else\
                self.math.create_forced_prize_extraction( self.state['data']['cards'], bet_args['name'] )

        
        self.state['data']['balls'] = l[0:NUM_NORMAL_BALLS]
        self.state['data']['extraballs'] = l[NUM_NORMAL_BALLS:(NUM_NORMAL_BALLS+NUM_EXTRA_BALLS)]
        self.internal_state['extraballs'] = l[NUM_NORMAL_BALLS:(NUM_NORMAL_BALLS+NUM_EXTRA_BALLS)]
        
        results = self.math.calc_prizes(self.state['data']['balls'],
                                        self.state['data']['cards'],
                                        self.state['data']['bet']/4)

        self.state['data']['winnings'] = results['card_wins']
        self.state["data"]["jackpot_wins"] = int(self.calc_jackpot_win(self.state['data']['bet']/4) if results['jackpot'] else 0)
        self.state['data']['total_winnings'] = sum(results['card_wins']) + self.state["data"]["jackpot_wins"]
        self.total_natural_wins = self.state['data']['total_winnings']
        if (results['has_extra']):
            self.state['data']['extra_cost'] = self.math.calc_extra_ball_price(results)
        elif ('extra_cost' in self.state['data']):
            self.state['data'].pop('extra_cost')

        
        self.new_state('game', ['bet', 'extra', 'end'] if (results['has_extra'] and self.internal_state['extraballs']) else ['bet', 'end'])
        
    # TODO: deduplicate some code in common with bet() sometime, will ya?
    def buy_extra_ball(self):
        
        if 'extra' not in self.state['actions']:
            return   # wtf1
        
        if self.state['name'] != 'game':
            return   # wtf2

        cost = int(self.state['data']['extra_cost'])
        creds = self.wallet.combined_credits()
        if( creds < cost ):
            return

        # not manipulating wallet directly anymore, only the rounds
        # self.wallet.charge_credits( cost )

        tx = rounds.build_transaction(rounds.round.TYPE_BET, "extra_ball", cost, "", {})
        self.curr_round.add_transaction(tx)
                
        self.state['data']['balls'].append(self.internal_state['extraballs'][0])
        self.state['data']['extraballs'] = self.internal_state['extraballs'][1:]
        self.internal_state['extraballs'] = self.internal_state['extraballs'][1:]
        
        newresults = self.math.calc_prizes(self.state['data']['balls'],
                                           self.state['data']['cards'],
                                           self.state['data']['bet']/4)
        if AGGRESSIVE_PRINTS: logger.debug("PRIZES ARE: "+str(newresults))
        self.state['data']['winnings'] = newresults['card_wins']
        self.state['data']['total_winnings'] = sum(newresults['card_wins']) + self.state['data']['jackpot_wins']
        if (newresults['has_extra']):
            self.state['data']['extra_cost'] = self.math.calc_extra_ball_price(newresults)
        elif ('extra_cost' in self.state['data']):
            self.state['data'].pop('extra_cost')
                
        self.new_state('game', ['extra', 'end'] if (newresults['has_extra'] and self.internal_state['extraballs']) else ['end'])
        

    def end_play(self):

        # let's finish the current round and send it up
        if self.curr_round:

            prizes = self.math.calc_prizes(self.state['data']['balls'],
                                           self.state['data']['cards'],
                                           self.state['data']['bet']/4)

            # iterate over all prizes and add them to round
            if AGGRESSIVE_PRINTS: logger.debug("PRIZE INFO:" + str(prizes))
            for card_idx in range(len(prizes["card_prizes"])):
                card_prizes = prizes["card_prizes"][card_idx]
                for prize in card_prizes:
                    if AGGRESSIVE_PRINTS: logger.debug(f"PRIZE IN CARD {card_idx}: "+str(prize))
                    tx = rounds.build_transaction(rounds.round.TYPE_PAYOUT, prize[0], int(prize[1]), f"prize {prize[0]} in card {card_idx+1}",
                                                  {"prize_name": prize[0],
                                                   "prize_payout": prize[1],
                                                   "prize_card": card_idx+1})
                    self.curr_round.add_transaction(tx)

            if self.state['data']['jackpot_wins']:
                jp_value = self.state['data']['jackpot_wins']
                tx = rounds.build_transaction(rounds.round.TYPE_PAYOUT, "JACKPOT", jp_value, "jackpot from cards "+repr(prizes["jackpot_cards"]), {"dummy":"dummy"})
                self.curr_round.add_transaction(tx)
                self.target_pot.pay_value(jp_value)

            # add game information to round
            round_data = {"balls": self.state['data']['balls'],
                          "extraballs":self.state['data']['extraballs'],
                          "cards": self.state['data']['cards'],
                          "total_natural_wins": self.total_natural_wins
                          }
            self.curr_round.extra_data = round_data

            self.curr_round.lobby_version = self.lobby_version
            self.curr_round.game_version = self.game_version

            if self.round_process_callback:
                self.round_process_callback(self.curr_round)

            # post round
            OutletNew.commit_round(self.wallet, self.rgs_session, self.curr_round)
            # round_outlet.commit_round(self.wallet, self.rgs_session, self.curr_round)
            self.curr_round = None
        else:
            logger.warning("[bingo] attempted to end_play with no current round")

    def new_state(self, name, actions):
        self.state['id'] = self.gen_state_id()
        self.state['name'] = name
        self.state['actions'] = actions


    def calc_jackpot_win(self, bet_per_card):
        if not self.target_pot:
            return 0

        bc = self.gamedefs["betcontrol"][str(self.wallet.denom)]

        bet_info = None
        for bet in bc["allowed_bets"]:
            if bet["amount"] <= bet_per_card:
                bet_info = bet

        frac = bet_info["jp_fraction"]
        return int(self.target_pot.value() * float(frac))


    def can_finish_game(self) -> bool:
        return self.state['name'] == 'idle' or 'end' in self.state['actions']

    def finish_game(self) -> bool:
        if( 'end' in self.state['actions'] ):
            self.do_action( "end", {}, self.state['id'] )
        return self.state['name'] == 'idle'


