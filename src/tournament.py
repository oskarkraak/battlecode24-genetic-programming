from collections import deque
from typing import List, Tuple

from src.battlecode_runner import run_battlecode
from src.util import timestamp
from concurrent.futures import ThreadPoolExecutor


def run_battle(bot1: str, bot2: str) -> Tuple[str, str]:
    """
    Run a single battle between two bots.
    Returns the winner and loser.
    """
    print(f"{timestamp()} Running battle: {bot1} vs {bot2}")
    result = run_battlecode(bot1, bot2)

    # Determine winner based on battle results
    if result == 1:
        print(f"{timestamp()} Battle finished: {bot1} won vs {bot2}")
        return bot1, bot2
    else:
        print(f"{timestamp()} Battle finished: {bot2} won vs {bot1}")
        return bot2, bot1

def run_double_elimination_tournament(names: List[str]) -> List[str]:
    """
    Run a double-elimination tournament and return the final rankings.
    """
    # Initialize brackets
    winners_bracket = deque(names)
    losers_bracket = deque()
    eliminated = []

    # While there's more than one bot in the winners' bracket
    while len(winners_bracket) + len(losers_bracket) > 1:
        print(f"Current Winners Bracket: {list(winners_bracket)}")
        print(f"Current Losers Bracket: {list(losers_bracket)}")

        # Winners' bracket matches
        while len(winners_bracket) > 1:
            bot1 = winners_bracket.popleft()
            bot2 = winners_bracket.popleft()
            winner, loser = run_battle(bot1, bot2)
            winners_bracket.append(winner)
            losers_bracket.append(loser)

        # If only one bot left in winners, keep it
        if winners_bracket:
            final_winner = winners_bracket.popleft()
        else:
            final_winner = None

        # Losers' bracket matches
        next_round_losers = deque()
        while len(losers_bracket) > 1:
            bot1 = losers_bracket.popleft()
            bot2 = losers_bracket.popleft()
            winner, loser = run_battle(bot1, bot2)
            next_round_losers.append(winner)
            eliminated.append(loser)

        # If one bot remains in losers, keep it for next round
        if losers_bracket:
            next_round_losers.append(losers_bracket.popleft())

        losers_bracket = next_round_losers

    # Final match between last winner and last loser
    if final_winner and losers_bracket:
        last_loser = losers_bracket.popleft()
        winner, loser = run_battle(final_winner, last_loser)
        eliminated.append(loser)
        eliminated.append(winner)  # Add the final winner last

    return eliminated[::-1]  # Return rankings in reverse order (winner last)

def run_one_game_tournament(names: List[str]) -> List[str]:
    """
    Returns the winners in the first half of the list and the losers in the second half.
    Can't handle uneven number of names.
    """
    winners = []
    losers = []
    pairs = [(names[i], names[i+1]) for i in range(0, len(names), 2)]

    with ThreadPoolExecutor() as executor:
        results = list(executor.map(lambda pair: run_battle(*pair), pairs))

    for winner, loser in results:
        winners.append(winner)
        losers.append(loser)

    return winners + losers
