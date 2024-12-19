from src.genetic_algorithm import genetic_programming
import os
import shutil

from src.util import timestamp

if __name__ == "__main__":
    # Delete all folders inside the 'gen' package
    print(f"{timestamp()} Deleting previous code...")
    battlecode_path = os.path.abspath("../battlecode24-scaffold/src/")
    for gen in range(1000):
        gen_folder_path = os.path.join(battlecode_path, "gen"+str(gen))
        if os.path.exists(gen_folder_path):
            for item in os.listdir(gen_folder_path):
                item_path = os.path.join(gen_folder_path, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)  # Delete the folder and its contents
    print(f"{timestamp()} Deleted previous code.")

    best_code = genetic_programming()
    print(f"{timestamp()} done :)")
