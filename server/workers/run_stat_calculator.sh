#!/bin/bash
#SBATCH --time=12:00:00
#SBATCH --mem=8000MB
#SBATCH --account=def-gabilode

module load flexiblas

~/.localpython/bin/python3 ./stat_calculator.py