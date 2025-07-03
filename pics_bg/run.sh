#!/bin/bash

# SLURM options:

#SBATCH --job-name=simulation_manager    # Job name
#SBATCH --ntasks=1                    # Execute a single task
#SBATCH --mem=7000                    # Memory in MB
#SBATCH --time=0-07:00:00             # Max time = 1 hour
#SBATCH --output=none   # Standard output log file
#SBATCH --error=none   # Standard error log file
./plot_snd_pics.exe
