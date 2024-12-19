import os
import subprocess
from typing import List
import platform

from src.mutatable import Mutatable
from src.template import template
from src.util import code_to_string, timestamp, analyze_output

# Paths
battlecode_path = os.path.abspath("../battlecode24-scaffold/src/")
gradle_path = os.path.abspath("../battlecode24-scaffold/")
gradle_executable = os.path.join(gradle_path, "gradlew.bat" if platform.system() == "Windows" else "gradlew")


def make_bot(gen: int, bot_name: str, java_code: List[Mutatable]) -> str:
    """
    Writes the bot into a file.

    :param gen: Generation of the bot
    :param bot_name: Name of the bot - arbitrary but unique within the generation
    :param java_code: Code for the bot
    :return: string containing the ID of the bot for execution
    """
    # Create folder
    gen = "gen" + str(gen)
    id = gen + "." + bot_name
    if not os.path.exists(gradle_executable):
        raise NotADirectoryError(f"Battlecode source not found at '{battlecode_path}'")
    package_path = os.path.join(battlecode_path, gen)
    package_path = os.path.join(package_path, bot_name)
    os.makedirs(package_path, exist_ok=True)
    java_file_path = os.path.join(package_path, "RobotPlayer.java")
    # Write the generated Java code
    generated_code = template.replace("[$CODE]", code_to_string(java_code)).replace("[$PACKAGE]", id)
    with open(java_file_path, "w") as file:
        file.write(generated_code)
        file.flush()
    print(f"{timestamp()} Generated code written to {java_file_path}")

    return id


def run_battlecode(bot1_name: str, bot2_name: str) -> int:
    """
    :return:
    """
    try:
        # Ensure gradle paths exist
        if not os.path.exists(gradle_executable):
            raise FileNotFoundError(f"Gradle wrapper not found at '{gradle_executable}'")

        print(f"{timestamp()} Starting gradle run...")

        # Run the Gradle 'run' task
        result = subprocess.run(
            [gradle_executable, "run", f"-PteamA={bot1_name}", f"-PteamB={bot2_name}", "--quiet"],
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
            return 0  # Penalize failures - would make sense if this was the fitness function, but doesn't

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
