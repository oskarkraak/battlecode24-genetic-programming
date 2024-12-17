import random
import subprocess
import os

# Define the components of a simple Java program
template = """
public class Program {
    public static int compute(int a, int b) {
        {code}
    }
}
"""

def generate_random_code():
    """Generate random Java code that performs simple operations on two integers."""
    operations = [
        "return a + b;",
        "return a - b;",
        "return a * b;",
        "return a / b;",
        "return a % b;",
        "return Math.max(a, b);",
        "return Math.min(a, b);"
    ]
    return random.choice(operations)

def fitness(java_code):
    """Evaluate the fitness of the Java code by compiling and running it."""
    filename = "Program.java"
    with open(filename, "w") as file:
        file.write(template.replace("{code}", java_code))

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

def mutate(code):
    """Mutate the Java code by randomly replacing operations."""
    return generate_random_code()

def crossover(code1, code2):
    """Crossover two Java codes (not meaningful in this simple case)."""
    return random.choice([code1, code2])

def genetic_programming():
    """Main loop for genetic programming."""
    population = [generate_random_code() for _ in range(10)]
    generations = 50

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
    print(template.replace("{code}", best_code))
