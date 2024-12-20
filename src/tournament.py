from collections import deque
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor

from src.battlecode_runner import run_battlecode
from src.util import timestamp

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
    Run a double-elimination tournament in parallel and return the final rankings.
    """
    # Initialize brackets
    winners_bracket = deque(names)
    losers_bracket = deque()
    eliminated = []

    with ThreadPoolExecutor() as executor:
        # While there is more than one bot remaining
        while len(winners_bracket) + len(losers_bracket) > 1:
            print(f"Current Winners Bracket: {list(winners_bracket)}")
            print(f"Current Losers Bracket: {list(losers_bracket)}")

            # Break if no actual matches remain to prevent infinite loops
            if len(winners_bracket) <= 1 and len(losers_bracket) <= 1:
                break

            # Winners' bracket matches
            winner_pairs = []
            bye_bot = None

            # Pair bots for the current round
            while len(winners_bracket) > 1:
                bot1 = winners_bracket.popleft()
                bot2 = winners_bracket.popleft()
                winner_pairs.append((bot1, bot2))

            # Handle odd number of bots: the last bot gets a bye
            if len(winners_bracket) == 1:
                bye_bot = winners_bracket.popleft()

            # Run the matches
            winner_results = list(executor.map(lambda pair: run_battle(*pair), winner_pairs))

            # Add match results to the next round
            for winner, loser in winner_results:
                winners_bracket.append(winner)
                losers_bracket.append(loser)

            # If a bot got a bye, it advances to the next round
            if bye_bot:
                print(f"{timestamp()} {bye_bot} advances due to a bye.")
                winners_bracket.append(bye_bot)

            # Losers' bracket matches
            loser_pairs = []
            next_round_losers = deque()

            while len(losers_bracket) > 1:
                bot1 = losers_bracket.popleft()
                bot2 = losers_bracket.popleft()
                loser_pairs.append((bot1, bot2))

            loser_results = list(executor.map(lambda pair: run_battle(*pair), loser_pairs))

            for winner, loser in loser_results:
                next_round_losers.append(winner)
                eliminated.append(loser)

            # If one bot remains in losers, keep it for next round
            if losers_bracket:
                next_round_losers.append(losers_bracket.popleft())

            losers_bracket = next_round_losers

    # Final match between last winner and last loser
    if len(winners_bracket) == 1 and len(losers_bracket) == 1:
        final_winner = winners_bracket.popleft()
        last_loser = losers_bracket.popleft()

        final_result = run_battle(final_winner, last_loser)
        winner, loser = final_result

        if winner == last_loser:  # Loser bracket's finalist wins the first match
            print(f"{timestamp()} Running a second match for the double-elimination final.")
            final_result = run_battle(final_winner, last_loser)  # Second match
            winner, loser = final_result

        final_winner = winner
        eliminated.append(loser)
    else:
        # In case only one bot remains in total, it is declared the winner
        final_winner = winners_bracket.popleft() if winners_bracket else losers_bracket.popleft()

    eliminated.append(final_winner)
    eliminated.reverse()
    return eliminated


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
