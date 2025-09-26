import random
import pickle
import os
from typing import List, Tuple, Optional

from src.bot_names import get_names
from src.mutatable import Mutatable
from src.mutatable_strings import actions, ifs
from src.battlecode_runner import make_bot, build_bots
from src.tournament import run_one_game_tournament, run_double_elimination_tournament
from src.util import timestamp


def generate_random_line() -> Mutatable:
    return Mutatable("action", random.choice(random.choice([actions, ifs])))


def generate_random_code(length=50) -> List[Mutatable]:
    code = []
    for i in range(length):
        code.append(generate_random_line())
    return code


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


def save_checkpoint(population: List[Tuple[str, List[Mutatable]]], generation: int, checkpoint_dir: str = "checkpoints") -> None:
    """
    Save the current population and generation to a checkpoint file.
    """
    os.makedirs(checkpoint_dir, exist_ok=True)
    checkpoint_data = {
        'population': population,
        'generation': generation,
        'random_state': random.getstate()
    }
    checkpoint_file = os.path.join(checkpoint_dir, f"checkpoint_gen_{generation}.pkl")
    with open(checkpoint_file, 'wb') as f:
        pickle.dump(checkpoint_data, f)
    print(f"{timestamp()} Saved checkpoint for generation {generation}")


def load_checkpoint(checkpoint_file: str) -> Tuple[List[Tuple[str, List[Mutatable]]], int]:
    """
    Load population and generation from a checkpoint file.
    Returns (population, generation)
    """
    with open(checkpoint_file, 'rb') as f:
        checkpoint_data = pickle.load(f)
    
    # Restore random state to ensure reproducibility
    random.setstate(checkpoint_data['random_state'])
    
    print(f"{timestamp()} Loaded checkpoint from generation {checkpoint_data['generation']}")
    return checkpoint_data['population'], checkpoint_data['generation']


def find_latest_checkpoint(checkpoint_dir: str = "checkpoints") -> Optional[str]:
    """
    Find the most recent checkpoint file in the checkpoint directory.
    Returns the path to the latest checkpoint file, or None if no checkpoints exist.
    """
    if not os.path.exists(checkpoint_dir):
        return None
    
    checkpoint_files = [f for f in os.listdir(checkpoint_dir) if f.startswith("checkpoint_gen_") and f.endswith(".pkl")]
    if not checkpoint_files:
        return None
    
    # Extract generation numbers and find the highest one
    generations = []
    for filename in checkpoint_files:
        try:
            gen_num = int(filename.replace("checkpoint_gen_", "").replace(".pkl", ""))
            generations.append((gen_num, filename))
        except ValueError:
            continue
    
    if not generations:
        return None
    
    latest_gen, latest_file = max(generations, key=lambda x: x[0])
    return os.path.join(checkpoint_dir, latest_file)


def fitness(java_codes: List[Tuple[str, List[Mutatable]]], generation: int) -> List[Tuple[int, List[Mutatable], str]]:
    """
    Evaluate the fitness of Java bots using a tournament.
    Bots are ranked based on their performance.
    """
    # Create bots/files
    result = []
    names = [name for name, _ in java_codes]
    for name, java_code in java_codes:
        make_bot(name, java_code)
        result.append((0, java_code, name))  # Initialize rank as 0
    build_bots()

    # Run the tournament
    rankings = run_one_game_tournament(names)

    # Update results with final ranks
    ranked_result = [
        (rank, java_codes[names.index(bot_name)][1], bot_name)
        for rank, bot_name in enumerate(rankings, start=1)
    ]

    return ranked_result


def genetic_programming(resume_from_checkpoint: bool = True, checkpoint_interval: int = 10):
    """
    Main loop for genetic programming with checkpointing support.
    
    Args:
        resume_from_checkpoint: If True, attempts to resume from the latest checkpoint
        checkpoint_interval: Save checkpoint every N generations
    """
    initial_population_size = 40
    population_size = 40
    generations = 500

    # Try to resume from checkpoint
    population = None
    start_generation = 0
    
    if resume_from_checkpoint:
        latest_checkpoint = find_latest_checkpoint()
        if latest_checkpoint:
            population, start_generation = load_checkpoint(latest_checkpoint)
            print(f"{timestamp()} Resuming from generation {start_generation}")
        else:
            print(f"{timestamp()} No checkpoint found, starting from scratch")
    
    # Initialize population if not loaded from checkpoint
    if population is None:
        names = get_names(initial_population_size)
        for i in range(len(names)):
            names[i] = "gen0." + names[i]
        population = [(names[i], generate_random_code()) for i in range(initial_population_size)]
        start_generation = 0

    # If we're resuming, first evaluate the fitness of the loaded generation
    if resume_from_checkpoint and population and start_generation > 0:
        print(f"{timestamp()} Evaluating fitness of loaded generation {start_generation}")
        scores = fitness(population, start_generation)
        scores.sort(key=lambda x: x[0])  # Sort by rank (ascending)
        print(f"Generation {start_generation}: Best Score: {scores[0][0]}")
        
        # Select the top individuals for the next generation
        number_of_top_individuals = int(population_size / 2)
        top_individuals = scores[:number_of_top_individuals]
        
        # Create the next generation
        next_generation = []
        next_generation.extend(
            (name.replace("gen" + str(start_generation), "gen" + str(start_generation+1)), code)
            for _, code, name in top_individuals
        )  # Preserve top individuals

        # Generate offspring for the remaining slots
        offspring = []
        while len(next_generation) + len(offspring) < population_size:
            if random.random() < 0.5:  # Mutation
                _, code, _ = random.choice(top_individuals)
                offspring.append(mutate(code))
            else:  # Crossover
                _, code1, _ = random.choice(top_individuals)
                _, code2, _ = random.choice(top_individuals)
                offspring.append(crossover(code1, code2))
        offspring_names = get_names(len(offspring))
        for i in range(len(offspring_names)):
            offspring_names[i] = "gen" + str(start_generation+1) + "." + offspring_names[i]
        for i in range(len(offspring)):
            next_generation.append((offspring_names[i], offspring[i]))

        population = next_generation
        start_generation += 1

    # Configurable: how often and how many games for best-of-N fight
    best_of_n_interval = checkpoint_interval  # Run after every checkpoint by default
    best_of_n_games = 10  # Number of games per match

    def best_of_n_fight(bot1: str, bot2: str, n: int = 10, label: str = "") -> None:
        from src.tournament import run_battle
        wins1, wins2 = 0, 0
        print(f"\n{timestamp()} Best of {n} match: {bot1} vs {bot2} {label}")
        for i in range(n):
            winner, loser = run_battle(bot1, bot2)
            if winner == bot1:
                wins1 += 1
            else:
                wins2 += 1
            print(f"Game {i+1}: Winner = {winner}")
        print(f"\n{timestamp()} Best of {n} result: {bot1} {wins1} - {wins2} {bot2} {label}")

    for generation in range(start_generation, generations):
        # Evaluate fitness of the population
        scores = fitness(population, generation)
        # Sort the scores explicitly by the fitness value (first element of the tuple)
        scores.sort(key=lambda x: x[0])  # Sort by rank (ascending)

        # Print the best score of the generation
        print(f"Generation {generation}: Best Score: {scores[0][0]}")

        # Save checkpoint at regular intervals
        if generation % checkpoint_interval == 0:
            save_checkpoint(population, generation)

        # Run best-of-N fight at the configured interval
        if best_of_n_interval > 0 and generation % best_of_n_interval == 0:
            # Pick the current best and a random bot from the population (excluding the best)
            current_best = scores[0][2]
            all_bots = [name for _, _, name in scores if name != current_best]
            if all_bots:
                random_bot = 'examplefuncsplayer'
                best_of_n_fight(current_best, random_bot, n=best_of_n_games, label=f"(gen {generation})")
            else:
                print(f"{timestamp()} No random bot available for best-of-N match at generation {generation}.")

        # Select the top individuals
        number_of_top_individuals = int(population_size / 2)
        top_individuals = scores[:number_of_top_individuals]

        # Create the next generation
        next_generation = []
        next_generation.extend(
            (name.replace("gen" + str(generation), "gen" + str(generation+1)), code)
            for _, code, name in top_individuals
        )  # Preserve top individuals

        # Generate offspring for the remaining slots
        offspring = []
        while len(next_generation) + len(offspring) < population_size:
            if random.random() < 0.5:  # Mutation
                _, code, _ = random.choice(top_individuals)
                offspring.append(mutate(code))
            else:  # Crossover
                _, code1, _ = random.choice(top_individuals)
                _, code2, _ = random.choice(top_individuals)
                offspring.append(crossover(code1, code2))
        offspring_names = get_names(len(offspring))
        for i in range(len(offspring_names)):
            offspring_names[i] = "gen" + str(generation+1) + "." + offspring_names[i]
        for i in range(len(offspring)):
            next_generation.append((offspring_names[i], offspring[i]))

        population = next_generation

    # Save final checkpoint
    save_checkpoint(population, generations)

    # Evaluate fitness of the final population
    scores = fitness(population, generations)
    # Sort the scores explicitly by the fitness value (first element of the tuple)
    scores.sort(key=lambda x: x[0])  # Sort by rank (ascending)

    # Extract the names of the top bots for the double-elimination tournament
    final_bot_names = [name for _, _, name in scores[:int(population_size/2)]]


    # Run the double-elimination tournament and print the top 3 winners
    print(f"{timestamp()} let's do a final double elimination tournament!")
    final_rankings = run_double_elimination_tournament(final_bot_names)

    print(f"\n{timestamp()} Final Top 3 Winners:")
    for rank, bot in enumerate(final_rankings[:3], start=1):
        print(f"Rank {rank}: {bot}")

    # Pick the overall winner and a random bot from the final population for a final best-of-N fight
    overall_winner = final_rankings[0]
    all_bots = [name for name, _, _ in scores if name != overall_winner]
    if all_bots:
        random_bot = 'examplefuncsplayer'
        best_of_n_fight(overall_winner, random_bot, n=best_of_n_games, label="(final)")
    else:
        print(f"{timestamp()} No random bot available for best-of-N match (final).")
