import random
from typing import List, Tuple

from src.bot_names import get_names
from src.mutatable import Mutatable
from src.mutatable_strings import actions, ifs
from src.battlecode_runner import make_bot
from src.tournament import run_one_game_tournament


def generate_random_line() -> Mutatable:
    return Mutatable("action", random.choice(random.choice([actions, ifs])))

def generate_random_code(length=50) -> List[Mutatable]:
    code = []
    for i in range(length):
        code.append(generate_random_line())
    return code

def fitness(java_codes: List[List[Mutatable]], generation: int) -> List[Tuple[int, List[Mutatable], str]]:
    """
    Evaluate the fitness of Java bots using a double-elimination tournament.
    Bots are ranked based on their performance.
    """

    # Create bots/files
    result = []
    names = get_names(len(java_codes))
    for i, java_code in enumerate(java_codes):
        name = names[i]
        make_bot(generation, name, java_code)
        result.append((0, java_code, name))  # Initialize rank as 0

    # Run the double-elimination tournament
    rankings = run_one_game_tournament(generation, names)

    # Update results with final ranks
    ranked_result = [
        (rank, java_codes[names.index(bot_name)], bot_name)
        for rank, bot_name in enumerate(rankings, start=1)
    ]

    return ranked_result

def mutate(code: List[Mutatable]) -> List[Mutatable]:
    new_code = []
    for mutatable in code:
        rand = random.random()
        if rand < 0.1:  # 10% chance to delete the line
            continue
        elif rand < 0.2:  # 10% chance to add a line
            new_code.append(mutatable)
            new_code.append(generate_random_line())
        elif rand < 0.4:  # 20% chance to mutate the line
            mutatable.mutate()
            new_code.append(mutatable)
        else:
            new_code.append(mutatable)
    return new_code

def crossover(code1: List[Mutatable], code2: List[Mutatable]) -> List[Mutatable]:
    """
    Perform uniform crossover with handling for differing code lengths.
    Each line has a 50% chance of being taken from either parent, with optional truncation or extension.
    """
    offspring = []
    max_len = min(len(code1), len(code2))  # Allow crossover up to the length of the shorter program

    # Mix lines probabilistically
    for i in range(max_len):
        offspring.append(random.choice([code1[i], code2[i]]))

    # Randomly add extra lines from the longer parent
    longer_parent = code1 if len(code1) > len(code2) else code2
    for i in range(max_len, len(longer_parent)):
        if random.random() < 0.5:  # 50% chance to include remaining lines
            offspring.append(longer_parent[i])

    return offspring

def genetic_programming():
    """Main loop for genetic programming."""
    initial_population_size = 4
    population_size = 4
    generations = 2

    population = [generate_random_code() for _ in range(initial_population_size)]

    for generation in range(generations):
        # Evaluate fitness of the population
        scores = fitness(population, generation)
        # Sort the scores explicitly by the fitness value (first element of the tuple)
        scores.sort(key=lambda x: x[0])  # Sort by rank (ascending)

        # Print the best score of the generation
        print(f"Generation {generation}: Best Score: {scores[0][0]}")

        # Select the top individuals
        number_of_top_individuals = int(len(population)/2)
        top_individuals = [code for _, code, _ in scores[:number_of_top_individuals]]

        # Create the next generation
        next_generation = top_individuals[:]
        while len(next_generation) < population_size:
            if random.random() < 0.5:  # Mutation
                next_generation.append(mutate(random.choice(top_individuals)))
            else:  # Crossover
                next_generation.append(crossover(random.choice(top_individuals),
                                                 random.choice(top_individuals)))

        population = next_generation

    # Return the best program
    return scores[0][1]

