#!/bin/bash

#SBATCH --time=99:59:00           # (HH:MM:SS)
#SBATCH --job-name=battlecode
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=50
#SBATCH --mem=128G

# Display job details
echo "Job ID: $SLURM_JOB_ID"
echo "Job Name: $SLURM_JOB_NAME"
echo "Node: $SLURM_NODELIST"
echo "CPUs per task: $SLURM_CPUS_PER_TASK"
echo "Memory: $SLURM_MEM_PER_NODE MB"
echo "Partition: $SLURM_JOB_PARTITION"
# Show detailed job information
scontrol show job $SLURM_JOB_ID

export PYTHONPATH=$(pwd)
cd battlecode24-scaffold
chmod +777 gradlew
cd ..
cd src
python3.11 __main__.py
