# Battlecode 2024 Genetic Programming

A genetic programming system that evolves Java bots for the Battlecode 2024 competition using evolutionary algorithms. The system generates, mutates, and selects bot behaviors through tournaments to create increasingly competitive AI players.

A test run (found in the `experiment-40x500.out` file) with a population of 40 over 500 generations failed to win against the random "examplfuncsplayer" even a single time in 10 matches. I thus consider this approach infeasible.
Further fine-tuning might be able to generate better results, or a full rework could be required. So far, it appears that **genetic programming is not adequate for Battlecode**.

## Prerequisites

- Python 3.11+
- Java (for Battlecode scaffold)
- Gradle (included in scaffold)
- Linux/Unix environment (for shell scripts)

## How It Works

### Genetic Algorithm Process

1. Initialization: Generate random population of Java bot behaviors
2. Evaluation: Run tournaments between bots to determine fitness rankings
3. Selection: Keep top-performing bots as parents
4. Reproduction: Create offspring through mutation and crossover
5. Repeat: Continue for many generations

### Bot Code Generation

- Uses predefined code templates with mutable actions
- Mutations can add, remove, or modify code lines
- Crossover combines code from two parent bots

### Tournament System

For efficiency, the tournament system was simplified to a single match per bot:

- All bots are paired up
- Each pair plays a match
- All winners are kept in the population, all losers are eliminated

Match results stored in `battlecode24-scaffold/matches/`.

The `tournament.py` also contains code for double elimination.

## Configuration

Key parameters in the genetic algorithm are configurable in `genetic_algorithm.py`:

- Population size
- Generation count
- Mutation rate
- Selection method
- Initial code length

Additionally, more actions can be added in `mutatable_strings.py`. These actions must be actual Battlecode bot actions. The specification can be found here: https://releases.battlecode.org/specs/battlecode24/3.0.5/specs.md.html.

## Checkpointing

The system automatically saves progress to resume interrupted runs:

- Automatic: Saves every N generations (configurable)
- Manual: Checkpoints stored in `src/checkpoints/`
- Recovery: Automatically resumes from latest checkpoint
- Format: Pickled Python objects with generation state

## Output

The system generates:

- Bot code: Java classes in `battlecode24-scaffold/src/gen*/`
- Match results: Battle outcomes in `battlecode24-scaffold/matches/`
- Checkpoints: Evolution state in `src/checkpoints/`
- Logs: Gradle logs and battle&tournament results
