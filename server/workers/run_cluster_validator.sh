#!/bin/bash
#SBATCH --time=12:00:00
#SBATCH --mem=4000MB
#SBATCH --account=def-gabilode

module load flexiblas

~/.localpython/bin/python3 ./cluster_validator.py