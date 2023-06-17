#!/bin/bash
#SBATCH --time=12:00:00
#SBATCH --mem=8000MB
#SBATCH --account=def-gabilode
#SBATCH --array=1-100

module load flexiblas

~/.localpython/bin/python3 ./detector.py $SLURM_ARRAY_TASK_ID