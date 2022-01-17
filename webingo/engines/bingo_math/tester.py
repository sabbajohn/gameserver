# NOTA DO TRELLO:
# Em geral as máquinas de bingo aceitam os seguintes parâmetros para o teste de matemática
# - perfil (para jogos com mais de 1)
# - cartelas abertas (ultimamente fixo em 4)
# - aposta (aposta por cartela)
# - bolas extras (quantas bolas extras vai comprar, quando tiver bola extra)
# - jogadas (quantas jogadas vai simular)
# Geralmente são feitos testes com 0 (zero) bolas extras e com todas bolas extras (11).
# Sendo que é necessário levar em consideração as regras de bola extra como no jogo normal,
# não simplesmente comprar 11 bolas em todas jogadas

# NOTA MINHA: perfil seria algo que vai em math_args,
# que por sua vez viria de gamedefs/configuração do server

import copy
import datetime as dt
import json
import locale
import logging
import subprocess as sp
import sys
import matplotlib.pyplot as pyplot

from tabulate import tabulate
from webingo.engines.bingo_math.factory import create_bingo_math

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

CREDIT_VALUE = 0.00001


def get_gamedefs(game):
    with open("res/games/" + game + "/manifest.json") as file:
        game_manifest = json.load(file)
        if "betcontrol" not in game_manifest["gamedefs"]:
            with open("res/bingo_betcontrol_default.json", "r") as file2:
                game_manifest["gamedefs"]["betcontrol"] = json.load(file2)
        return game_manifest["gamedefs"]


def get_betcontrol_defaults():
    with open("res/bingo_betcontrol_default.json") as file:
        betcontrol = json.load(file)
        return betcontrol


def get_jackpot_defaults():
    with open("res/jackpot_defaults.json") as file:
        conf = json.load(file)
        return conf


# this I stole from stackoverflow :)
# https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', print_end="\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bars = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} [[{bars}]] {percent}% {suffix}', end=print_end, flush=True)
    # Print New Line on Complete
    if iteration == total:
        print()


# Formats an alpha (0.0 to 1.0) into a percentage
def strpct(alpha):
    return "{0:.2f}%".format(100.0*alpha)


def getpct(src, num, denom):
    return strpct(float(src[num])/float(src[denom]))


# Adds thousands separator to a large number
def strthou(val):
    if isinstance(val, int):
        return "{:,}".format(val)
    return "{:,.2f}".format(val)


def strusd(val):
    return "USD "+strthou(float(val)*CREDIT_VALUE)


def calc_prize_stats(pinfo, prize_data, num_plays, accum):

    ret = []
    num_plays = float(num_plays)

    # let's add jackpot information to pinfo
    pinfo["JACKPOT"] = {
        "count": accum["plays_with_jackpot"],
        "plays": accum["plays_with_jackpot"],
        "totals": accum["total_won_jackpots"],
    }

    # we return a list of lists
    # the inner lists are stats for a prize,
    # and are laid out as such:
    # prize_name | count | count% | wins | plays | wins%

    total_prize_wins = 0
    total_prize_count = 0

    for prize in pinfo:
        total_prize_wins += pinfo[prize]["totals"]
        total_prize_count += pinfo[prize]["count"]

    prizenames = ["TOTALS"] + list(prize_data.keys()) + ["JACKPOT"]

    for prize in prizenames:
        if prize == "TOTALS":
            ret.append([prize, total_prize_count, "100%",
                        strthou(total_prize_wins), "n/a", "100%"])
        elif prize not in pinfo:
            ret.append([prize, 0, 0.0, 0, 0.0, 0.0, ])
        else:
            info = pinfo[prize]
            count = info["count"]
            wins = info["totals"]

            countpct = strpct(count/float(total_prize_count)) if total_prize_count else "-"

            play_interval = "{:.2f}".format(num_plays/float(count)) if count else "-"

            winspct = strpct(wins/float(total_prize_wins)) if total_prize_wins else "-"

            ret.append([prize, count, countpct, strthou(wins), play_interval, winspct, ])

    ret.sort(key=lambda t: -prizenames.index(t[0]), reverse=False)

    for prize in ret:
        prize[0] = prize[0].upper()
    return ret


def perform_math_test(math_id, math_args={}, num_plays=100000, bet_per_card=50, extras_to_buy=11):

    num_cards = 4
    gamedefs: dict = get_gamedefs(math_args['game_name'])
    math = create_bingo_math(math_id, gamedefs, **math_args)
    prize_data = math.prizelist

    betcontrol = gamedefs.get("betcontrol", None)
    if not betcontrol:
        betcontrol = get_betcontrol_defaults()
    betcontrol = betcontrol["CRE"]

    bet_jp_fraction = None
    for allowed in betcontrol["allowed_bets"]:
        if allowed["amount"] == bet_per_card:
            bet_jp_fraction = allowed["jp_fraction"]
    if bet_jp_fraction is None:
        print("This bet value [" + str(bet_per_card) +"] is not allowed by the bet control configuration!")
        print(json.dumps(betcontrol["allowed_bets"], indent=2, sort_keys=True))
        sys.exit(-1)

    jp_config = get_jackpot_defaults()
    jp_curr_value = float(jp_config["min_value"])
    jp_feed_fraction = float(jp_config["fraction"])
    jp_historical_max = jp_curr_value

    commit = "(unknown)"
    try:
        commit = sp.check_output("git rev-parse --short HEAD".split())
    except:
        pass
    today = dt.date.today()

    print("\n******************************************************************************")
    print("PARAMETROS DE TESTE")
    print(f"JOGO:       {math_args['game_name'].replace('_',' ').title()}")
    print(f"MATEMATICA: {math_id}")
    print(f"JOGADAS:    {strthou(num_plays)}")
    print(f"EXTRA:      {extras_to_buy}")
    print(f"APOSTA:     {bet_per_card} x {num_cards} = {strthou(bet_per_card*num_cards)}")
    print(f"CREDITO:    ${CREDIT_VALUE:.5f}")
    print(f"JACKPOT:    {strthou(int(jp_curr_value))} x {strthou(100.0 * bet_jp_fraction)}% = {strthou(int(bet_jp_fraction * jp_curr_value))}")
    print(f"COMMIT:     {commit.decode().split()[0]}")
    print(f"DATA:       {today.strftime('%d %b %Y')}")
    print("******************************************************************************\n")

    accum = {
        "plays_total": 0,
        "plays_with_extra": 0,
        "plays_with_prize": 0,
        "plays_with_jackpot": 0,
        "extra_balls_bought": 0,
        "total_spent": 0,
        "total_won": 0,
        "total_spent_naturals": 0,
        "total_won_naturals": 0,
        "total_spent_extras": 0,
        "total_won_extras": 0,
        "total_won_jackpots": 0
    }

    pinfo = {}  # accumulator for prize specifics

    start_t = dt.datetime.now()

    print_progress_bar(0, num_plays, prefix='Progress:', suffix='Complete', length=50)

    for play_index in range(num_plays):

        if not play_index % (num_plays / 100):
            print_progress_bar(play_index, num_plays, prefix='Progress:', suffix='Complete', length=50)

        cards = math.create_series(num_cards)
        extraction = math.create_extraction(cards)
        natural_balls = extraction[0:math.naturals]
        extra_balls = extraction[math.naturals:math.naturals+math.extras]

        natural_results = math.calc_prizes(natural_balls, cards, bet_per_card)

        remaining_extras = extras_to_buy
        curr_balls = copy.copy(natural_balls)
        curr_results = natural_results
        total_play_extra_cost = 0

        while remaining_extras:
            if not curr_results["has_extra"]:
                break
            total_play_extra_cost += math.calc_extra_ball_price(curr_results)
            curr_balls.append(extra_balls[extras_to_buy-remaining_extras])
            remaining_extras -= 1
            curr_results = math.calc_prizes(curr_balls, cards, bet_per_card)

        total_spent = num_cards * bet_per_card + total_play_extra_cost
        jp_curr_value += total_spent * jp_feed_fraction

        if jp_curr_value > jp_config["max_value"]:
            jp_curr_value = jp_config["max_value"]

        if jp_curr_value > jp_historical_max:
            jp_historical_max = jp_curr_value

        won_jackpot = False
        jackpot_wins = 0

        if natural_results["jackpot"]:
            # now we deal with the player winning a jackpot
            won_jackpot = True
            jackpot_wins = int(bet_jp_fraction * jp_curr_value)
            jp_curr_value -= jackpot_wins
            if jp_curr_value < jp_config["min_value"]:
                jp_curr_value = jp_config["min_value"]
            accum["total_won_jackpots"] += jackpot_wins

        won_prize = bool(won_jackpot or sum(curr_results["card_wins"]))

        accum["plays_total"] += 1
        accum["plays_with_extra"] += 1 if natural_results["has_extra"] else 0
        accum["plays_with_jackpot"] += 1 if won_jackpot else 0
        accum["extra_balls_bought"] += extras_to_buy - remaining_extras
        accum["plays_with_prize"] += 1 if won_prize else 0
        accum["total_spent"] += total_spent
        accum["total_won"] += sum(curr_results["card_wins"]) + jackpot_wins
        accum["total_spent_naturals"] += num_cards * bet_per_card
        accum["total_won_naturals"] += sum(natural_results["card_wins"]) + jackpot_wins
        accum["total_spent_extras"] += total_play_extra_cost
        accum["total_won_extras"] += sum(curr_results["card_wins"]) - sum(natural_results["card_wins"])

        play_prizes = set()

        # for every card prize data
        for card in curr_results["card_prizes"]:
            # for every prize in this card
            for prize in card:
                pname = prize[0]
                pwon = prize[1]
                play_prizes.add(pname)

                if pname in pinfo:
                    pinfo[pname]["count"] += 1
                    pinfo[pname]["totals"] += pwon
                else:
                    pinfo[pname] = {
                        "count": 1,
                        "totals": pwon,
                        "plays": 0  # will soon receive the count
                    }

        for pname in play_prizes:
            pinfo[pname]["plays"] += 1

    # Done simulating plays
    print_progress_bar(num_plays, num_plays, prefix='Progress:', suffix='Complete', length=50)

    end_t = dt.datetime.now()

    prize_stats = calc_prize_stats(pinfo, prize_data, num_plays, accum)

    tbl = []
    for index in accum:  # add details column in accumulators
        thousands_fmt = True
        detail = "-"
        if index == "plays_with_extra":
            detail = getpct(accum, "plays_with_extra", "plays_total")
        elif index == "plays_with_prize":
            detail = getpct(accum, "plays_with_prize", "plays_total")
        elif index == "plays_with_jackpot":
            if accum["plays_with_jackpot"] > 0:
                detail = "every {:.2f} plays".format(
                    accum["plays_total"] / accum["plays_with_jackpot"])
            else:
                detail = "every {:.2f} plays".format(0)
        elif index == "extra_balls_bought":
            detail = "{:.3f} per play and {:.3f} per play w/extras".\
                format(accum["extra_balls_bought"]/float(accum["plays_total"]),
                       accum["extra_balls_bought"]/float(accum["plays_with_extra"]))
        #elif index == "total_spent":
        #    detail = strusd(accum["total_spent"])
        elif index == "total_won":
            detail = getpct(accum, "total_won", "total_spent")
        #elif index == "total_spent_naturals":
        #    detail = getpct(accum, "total_spent_naturals", "total_spent")
        elif index == "total_won_naturals":
            detail = "{} with jackpots, {} without".format(
                getpct(accum, "total_won_naturals", "total_spent_naturals"),
                strpct((accum["total_won_naturals"]-accum["total_won_jackpots"])/float(accum["total_spent_naturals"])))
        elif index == "total_spent_extras" and accum["extra_balls_bought"]:
            avg_extra = accum["total_spent_extras"] /  float(accum["extra_balls_bought"])
            # detail = "{:.3f} ({}) per extra on avg.".format(avg_extra, strusd(avg_extra))
            detail = "{:.3f} per extra on avg.".format(avg_extra)
        elif index == "total_won_extras" and accum["total_spent_extras"]:
            detail = strpct(accum["total_won_extras"] /
                            float(accum["total_spent_extras"]))
        elif index == "total_won_jackpots":
            detail = "{} total, {} of naturals".format(
                getpct(accum, "total_won_jackpots", "total_won"),
                getpct(accum, "total_won_jackpots", "total_won_naturals"))

        tbl.append(
            [index.upper(), accum[index] if not thousands_fmt else strthou(accum[index]), detail])

    print("\n\n")
    hdr = ("Contador", "Valor", "Info")
    print(tabulate(tbl, headers=hdr, floatfmt=".3f", tablefmt="fancy_grid", colalign=("left", "right", "left")))

    print("\n\n")
    hdr = ("Prize", "Count", "Count %", "Wins", "Plays", "Wins %")
    print(tabulate(prize_stats, headers=hdr, floatfmt=".3f", tablefmt="fancy_grid", colalign=("left", "right", "right", "right", "right", "right")))

    print("\n******************************************************************************")
    print("Tempo gasto: {}".format(end_t-start_t))
    print("******************************************************************************\n")

    labels = [prize[0] for prize in prize_stats[:-1]] # nomes; :-1 == todos menos o ultimo, TOTAL

    sizes = [str(prize[3]) for prize in prize_stats[:-1]]  # pagos fixed as string; :-1 == todos menos o ultimo, TOTAL

    # remove thousand separator, matplot does not accept this
    for index in range(len(sizes)):
        sizes[index] = sizes[index].replace(',', '')

    figure_name = "teste_" + math_args['game_name'] + "_" + commit.decode().split()[0] + ".png"

    mpl_logger = logging.getLogger('matplotlib')
    mpl_logger.setLevel(logging.WARNING)

    figure, axis = pyplot.subplots()
    figure.suptitle('DISTRIBUIÇÃO DE PREMIOS', fontsize=14, fontweight='bold')
    axis.pie(sizes, labels=labels, startangle=90, counterclock=False)
    axis.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    pyplot.savefig(figure_name)


if __name__ == "__main__":
    # print(sys.argv)
    model = sys.argv[1]
    game_name = sys.argv[2]
    rounds = int(sys.argv[3])
    bet = int(sys.argv[4])
    extras = int(sys.argv[5])
    perform_math_test(model, {"game_name": game_name}, rounds, bet, extras)
