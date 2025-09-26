#!/usr/bin/env python3

"""
Checkpoint manager for the genetic programming system.
Provides utilities to list, inspect, and manage checkpoint files.
"""

import os
import pickle
import argparse
from typing import List, Tuple
from src.genetic_algorithm import find_latest_checkpoint
from src.util import timestamp


def list_checkpoints(checkpoint_dir: str = "checkpoints") -> List[Tuple[int, str]]:
    """
    List all available checkpoints.
    Returns a list of (generation, filename) tuples sorted by generation.
    """
    if not os.path.exists(checkpoint_dir):
        return []
    
    checkpoint_files = [f for f in os.listdir(checkpoint_dir) if f.startswith("checkpoint_gen_") and f.endswith(".pkl")]
    
    generations = []
    for filename in checkpoint_files:
        try:
            gen_num = int(filename.replace("checkpoint_gen_", "").replace(".pkl", ""))
            generations.append((gen_num, filename))
        except ValueError:
            continue
    
    return sorted(generations, key=lambda x: x[0])


def inspect_checkpoint(checkpoint_file: str):
    """
    Inspect the contents of a checkpoint file.
    """
    try:
        with open(checkpoint_file, 'rb') as f:
            checkpoint_data = pickle.load(f)
        
        generation = checkpoint_data.get('generation', 'Unknown')
        population = checkpoint_data.get('population', [])
        
        print(f"Checkpoint: {checkpoint_file}")
        print(f"Generation: {generation}")
        print(f"Population size: {len(population)}")
        
        if population:
            print(f"Bot names:")
            for name, _ in population:
                print(f"  - {name}")
        
        print()
        
    except Exception as e:
        print(f"Error reading checkpoint {checkpoint_file}: {e}")


def delete_checkpoint(checkpoint_file: str):
    """
    Delete a specific checkpoint file.
    """
    try:
        os.remove(checkpoint_file)
        print(f"Deleted checkpoint: {checkpoint_file}")
    except Exception as e:
        print(f"Error deleting checkpoint {checkpoint_file}: {e}")


def clean_old_checkpoints(checkpoint_dir: str = "checkpoints", keep_last: int = 3):
    """
    Clean old checkpoints, keeping only the most recent ones.
    """
    checkpoints = list_checkpoints(checkpoint_dir)
    
    if len(checkpoints) <= keep_last:
        print(f"Only {len(checkpoints)} checkpoints found, nothing to clean.")
        return
    
    to_delete = checkpoints[:-keep_last]  # All except the last N
    
    print(f"Deleting {len(to_delete)} old checkpoints (keeping {keep_last} most recent):")
    
    for gen, filename in to_delete:
        filepath = os.path.join(checkpoint_dir, filename)
        print(f"  Deleting generation {gen}: {filename}")
        delete_checkpoint(filepath)


def main():
    parser = argparse.ArgumentParser(description='Manage genetic programming checkpoints')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all checkpoints')
    list_parser.add_argument('--dir', default='checkpoints', help='Checkpoint directory')
    
    # Inspect command
    inspect_parser = subparsers.add_parser('inspect', help='Inspect a checkpoint')
    inspect_parser.add_argument('checkpoint', nargs='?', help='Checkpoint file to inspect (or "latest")')
    inspect_parser.add_argument('--dir', default='checkpoints', help='Checkpoint directory')
    
    # Delete command  
    delete_parser = subparsers.add_parser('delete', help='Delete a checkpoint')
    delete_parser.add_argument('checkpoint', help='Checkpoint file to delete')
    
    # Clean command
    clean_parser = subparsers.add_parser('clean', help='Clean old checkpoints')
    clean_parser.add_argument('--keep', type=int, default=3, help='Number of recent checkpoints to keep')
    clean_parser.add_argument('--dir', default='checkpoints', help='Checkpoint directory')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        checkpoints = list_checkpoints(args.dir)
        if not checkpoints:
            print(f"No checkpoints found in {args.dir}")
        else:
            print(f"Found {len(checkpoints)} checkpoints:")
            for gen, filename in checkpoints:
                filepath = os.path.join(args.dir, filename)
                size = os.path.getsize(filepath) / 1024  # KB
                print(f"  Generation {gen:2d}: {filename} ({size:.1f} KB)")
            
            latest = find_latest_checkpoint(args.dir)
            if latest:
                print(f"\nLatest: {os.path.basename(latest)}")
    
    elif args.command == 'inspect':
        if args.checkpoint == 'latest' or args.checkpoint is None:
            checkpoint_file = find_latest_checkpoint(args.dir)
            if not checkpoint_file:
                print(f"No checkpoints found in {args.dir}")
                return
        else:
            checkpoint_file = args.checkpoint
            if not os.path.isabs(checkpoint_file):
                checkpoint_file = os.path.join(args.dir, checkpoint_file)
        
        inspect_checkpoint(checkpoint_file)
    
    elif args.command == 'delete':
        delete_checkpoint(args.checkpoint)
    
    elif args.command == 'clean':
        clean_old_checkpoints(args.dir, args.keep)
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
