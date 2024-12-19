import random
from typing import List

# Define the lists
adjectives = [
    "Agile", "Amazing", "Bold", "Brave", "Bright", "Calm", "Clever", "Curious", "Daring",
    "Dazzling", "Dynamic", "Energetic", "Fantastic", "Fearless", "Fierce", "Friendly",
    "Generous", "Gentle", "Glorious", "Happy", "Helpful", "Heroic", "Incredible", "Intelligent",
    "Jolly", "Kind", "Lively", "Mighty", "Nimble", "Optimistic", "Peaceful", "Powerful",
    "Quick", "Radiant", "Reliable", "Resourceful", "Sharp", "Shiny", "Silent", "Skillful",
    "Smart", "Splendid", "Strong", "Superb", "Swift", "Thoughtful", "Vibrant", "Wise",
    "Witty", "Zesty"
]

nouns = [
    "Falcon", "Tiger", "Eagle", "Panther", "Hawk", "Wolf", "Bear", "Lynx", "Cheetah", "Lion",
    "Circuit", "Engine", "Gear", "Byte", "Matrix", "Spark", "Chip", "Shield", "Dynamo", "Beacon"
]

# Generate all combinations
all_combinations = [f"{adj}{noun}" for adj in adjectives for noun in nouns]

def get_names(n: int) -> List[str]:
    # Select n unique combinations
    if n > len(all_combinations):
        raise ValueError("n cannot be greater than the total number of combinations")

    unique_combinations = random.sample(all_combinations, n)
    return unique_combinations
