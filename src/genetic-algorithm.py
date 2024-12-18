import random
import subprocess
import re
import os
from typing import List, Dict
import platform
import time

from template import template
from mutatable_strings import *


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

def analyze_output(output: str) -> float:
    """
    Analyze the output of the program to determine if team A won.
    Fitness is 1 if 'A' wins, otherwise 0.
    """
    # Check for match result
    if "(A) wins" in output:
        return 1.0
    else:
        return 0.0

def timestamp() -> str:
    """Return the current time as a formatted string."""
    return time.strftime("[%Y-%m-%d %H:%M:%S]")

def fitness(java_code: List[Mutatable]) -> float:
    """
    Evaluate the fitness of the Java code by writing it to the Battlecode scaffold,
    running it via Gradle, and analyzing the output.
    Fitness = 1 if team A wins, otherwise 0.
    """
    # Paths
    battlecode_path = os.path.abspath("./battlecode24-scaffold/src/genalgplayer/")
    java_file_path = os.path.join(battlecode_path, "RobotPlayer.java")
    gradle_path = os.path.abspath("./battlecode24-scaffold/")
    gradle_executable = os.path.join(gradle_path, "gradlew.bat" if platform.system() == "Windows" else "gradlew")

    try:
        # Ensure paths exist
        os.makedirs(battlecode_path, exist_ok=True)
        if not os.path.exists(gradle_executable):
            raise FileNotFoundError(f"Gradle wrapper not found at '{gradle_executable}'")

        # Write the generated Java code
        generated_code = template.replace("{code}", code_to_string(java_code))
        #print("Generated Java Code:\n", generated_code)  # Debug
        with open(java_file_path, "w") as file:
            file.write(generated_code)
            file.flush()

        print(f"{timestamp()} Generated code written to {java_file_path}")
        print(f"{timestamp()} Starting gradle run...")

        # Run the Gradle 'run' task
        result = subprocess.run(
            [gradle_executable, "run", "--quiet"],
            cwd=gradle_path,
            capture_output=True,
            text=True,
            timeout=300
        )

        print(f"{timestamp()} Finished gradle run.")

        # Check if Gradle succeeded
        if result.returncode != 0:
            print(f"{timestamp()} Gradle build failed. Return code: {result.returncode}")
            print(f"{timestamp()} Error Output:\n{result.stderr}")
            return 0  # Penalize failures

        # Analyze the output for a win
        output = result.stdout.strip()
        result = analyze_output(output)
        print(f"{timestamp()} Program output: {result}")
        return result

    except subprocess.TimeoutExpired:
        print(f"{timestamp()} Gradle run task timed out.")
        return 0  # Penalize timeouts
    except Exception as e:
        print(f"{timestamp()} Error during fitness evaluation: {e}")
        return 0  # Penalize any other issues
    finally:
        pass


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
    population_size = 1
    generations = 1

    population = [generate_random_code() for _ in range(population_size)]

    for generation in range(generations):
        # Evaluate fitness of the population
        scores = [(fitness(code), code) for code in population]
        # Sort the scores explicitly by the fitness value (first element of the tuple)
        scores.sort(key=lambda x: x[0], reverse=True)

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
    print("done :)")
