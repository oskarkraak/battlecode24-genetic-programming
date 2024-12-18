import os
import subprocess
from typing import List
import platform

from src.mutatable import Mutatable
from src.template import template
from src.util import code_to_string, timestamp, analyze_output


def run_battlecode(java_code: List[Mutatable]) -> int:
    # Paths
    battlecode_path = os.path.abspath("../battlecode24-scaffold/src/genalgplayer/")
    java_file_path = os.path.join(battlecode_path, "RobotPlayer.java")
    gradle_path = os.path.abspath("../battlecode24-scaffold/")
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