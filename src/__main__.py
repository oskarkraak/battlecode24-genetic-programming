from src.genetic_algorithm import genetic_programming
import os
import shutil
import argparse

from src.util import timestamp

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run genetic programming with checkpointing support')
    parser.add_argument('--no-resume', action='store_true', 
                       help='Start from scratch instead of resuming from checkpoint')
    parser.add_argument('--checkpoint-interval', type=int, default=5,
                       help='Save checkpoint every N generations (default: 5)')
    parser.add_argument('--clean', action='store_true',
                       help='Clean previous code and checkpoints before starting')
    
    args = parser.parse_args()
    
    # Clean previous code and checkpoints if requested
    if args.clean:
        print(f"{timestamp()} Deleting previous code...")
        battlecode_path = os.path.abspath("../battlecode24-scaffold/src/")
        for gen in range(1000):
            gen_folder_path = os.path.join(battlecode_path, "gen"+str(gen))
            if os.path.exists(gen_folder_path):
                for item in os.listdir(gen_folder_path):
                    item_path = os.path.join(gen_folder_path, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)  # Delete the folder and its contents
        
        # Also clean checkpoints
        if os.path.exists("checkpoints"):
            shutil.rmtree("checkpoints")
            print(f"{timestamp()} Deleted checkpoints directory.")
        
        print(f"{timestamp()} Deleted previous code.")
    elif not args.no_resume:
        # Only clean previous code if we're not resuming, but keep checkpoints
        print(f"{timestamp()} Deleting previous code (keeping checkpoints)...")
        battlecode_path = os.path.abspath("../battlecode24-scaffold/src/")
        for gen in range(1000):
            gen_folder_path = os.path.join(battlecode_path, "gen"+str(gen))
            if os.path.exists(gen_folder_path):
                for item in os.listdir(gen_folder_path):
                    item_path = os.path.join(gen_folder_path, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)  # Delete the folder and its contents
        print(f"{timestamp()} Deleted previous code.")

    best_code = genetic_programming(
        resume_from_checkpoint=not args.no_resume,
        checkpoint_interval=args.checkpoint_interval
    )
    print(f"{timestamp()} done :)")
