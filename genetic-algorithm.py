import random
import subprocess
import re
import os
from typing import List, Dict

from template import template

actions = [
    "if (rc.canBuild([$TRAP1], rc.getLocation().subtract([$DIR1]))) rc.build([$TRAP1], rc.getLocation().subtract([$DIR1]));",
]

directions = [
    "directions[0]",
    "directions[1]",
    "directions[2]",
    "directions[3]",
    "directions[4]",
    "directions[5]",
    "directions[6]",
    "directions[7]",
]

trap_type = [
    "TrapType.EXPLOSIVE",
    "TrapType.STUN",
    "TrapType.WATER",
]

ifs = [
    "if ([$INT1] > [$INT2]) [$ACTION1]",
    "if ([$INT1] == [$INT2]) [$ACTION1]",
    "if ([$INT1] != [$INT2]) [$ACTION1]",
    "if ([$INT1] > [$INT2]) [$IF1]",
    "if ([$INT1] == [$INT2]) [$IF1]",
    "if ([$INT1] != [$INT2]) [$IF1]"
]

ints = [
    "rc.getMapHeight()",
    "rc.getMapWidth()",
    "rc.getRoundNum()",
    "GameConstants.SETUP_ROUNDS",
]

mapping = [
    ("INT", "int", ints),
    ("ACTION", "action", actions),
    ("IF", "if", ifs),
    ("DIR", "direction", directions),
    ("TRAP", "trap_type", trap_type),
]


class Mutatable:
    def __init__(self, type: str, value: str):
        self.type = type
        self.value = value
        self.sub_mutatables: Dict[str, Mutatable] = {}
        self.detect_required_sub_mutatables()

def detect_required_sub_mutatables(self) -> None:
    """
    Detect placeholders like [$INTx], [$ACTIONx], etc., in the value
    and map them dynamically using the 'mapping' list.
    """
    matches = re.findall(r'\[\$(\w+)\]', self.value)

    for match in matches:
        if match not in self.sub_mutatables:  # Ensure no duplicate processing
            for placeholder, mutatable_type, options in mapping:
                if match.startswith(placeholder):
                    self.sub_mutatables[match] = Mutatable(mutatable_type, random.choice(options))
                    break
            else:
                raise RuntimeError(f"Unknown placeholder type: {match}")

    def mutate(self):
        """
        Mutate the sub-mutatables by randomly replacing or mutating them.
        """
        for key, sub_mutatable in list(self.sub_mutatables.items()):
            if random.random() < 0.2:  # 20% chance to replace the sub-mutable
                if key.startswith("INT"):
                    self.sub_mutatables[key] = Mutatable("int", random.choice(ints))
                elif key.startswith("ACTION"):
                    self.sub_mutatables[key] = Mutatable("action", random.choice(actions))
                elif key.startswith("DIR"):
                    self.sub_mutatables[key] = Mutatable("direction", random.choice(directions))
                elif key.startswith("IF"):
                    self.sub_mutatables[key] = Mutatable("if", random.choice(ifs))
            else:
                sub_mutatable.mutate()  # Recursively mutate existing sub-mutatables

    def __str__(self):
        result = self.value
        placeholders = re.findall(r'\[\$(\w+)\]', self.value)

        # Replace all placeholders using the sub-mutatables map
        for placeholder in placeholders:
            if placeholder in self.sub_mutatables:
                result = result.replace(f"[${placeholder}]", str(self.sub_mutatables[placeholder]), 1)
            else:
                raise RuntimeError(f"Missing sub-mutable for placeholder: {placeholder}")

        return result

def generate_random_line() -> Mutatable:
    return Mutatable("action", random.choice(random.choice([actions, ifs])))

def generate_random_code(length=50) -> List[Mutatable]:
    code = []
    for i in range(length):
        code.append(generate_random_line())
    return code

def code_to_string(code: List[Mutatable]) -> str:
    """Convert a list of Mutatable objects into a string representation."""
    return "\n".join(str(mutatable) for mutatable in code)

def fitness(java_code):
    """Evaluate the fitness of the Java code by compiling and running it."""

    filename = "Program.java"
    with open(filename, "w") as file:
        file.write(template.replace("{code}", code_to_string(java_code)))
    """
    try:
        # Compile the Java program
        subprocess.run(["javac", filename], check=True)
        # Run the compiled program with test inputs
        results = []
        for a, b in [(1, 2), (3, 5), (-1, -3), (10, 5)]:
            result = subprocess.run(["java", "-cp", ".", "Program"],
                                    input=f"{a}\n{b}\n".encode(),
                                    capture_output=True, check=True)
            results.append(int(result.stdout.strip()))

        # Target behavior: summing two numbers
        target = [a + b for a, b in [(1, 2), (3, 5), (-1, -3), (10, 5)]]
        score = -sum(abs(r - t) for r, t in zip(results, target))
        return score

    except Exception as e:
        # Penalize code that doesn't compile or run correctly
        return -float('inf')

    finally:
        # Clean up
        if os.path.exists(filename):
            os.remove(filename)
        if os.path.exists("Program.class"):
            os.remove("Program.class")
    """
    return random.random()

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
    population = [generate_random_code() for _ in range(10)]
    generations = 1 #50

    for generation in range(generations):
        # Evaluate fitness of the population
        scores = [(fitness(code), code) for code in population]
        scores.sort(reverse=True)

        # Print the best score of the generation
        print(f"Generation {generation}: Best Score: {scores[0][0]}")

        # Select the top individuals
        top_individuals = [code for _, code in scores[:5]]

        # Create the next generation
        next_generation = top_individuals[:]
        while len(next_generation) < 10:
            if random.random() < 0.5:  # Mutation
                next_generation.append(mutate(random.choice(top_individuals)))
            else:  # Crossover
                next_generation.append(crossover(random.choice(top_individuals),
                                                 random.choice(top_individuals)))

        population = next_generation

    # Return the best program
    return scores[0][1]

if __name__ == "__main__":
    best_code = genetic_programming()
    print("Best Java Program:")
    print(template.replace("{code}", code_to_string(best_code)))
