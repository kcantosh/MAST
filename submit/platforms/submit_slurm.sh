#!/bin/bash

#SBATCH -t 1:00:00
#SBATCH -J mastmon
#SBATCH -N 1
#SBATCH -n 1
#SBATCH --ntasks-per-node=1
python runmast.py >> $MAST_CONTROL/mastoutput 2> $MAST_CONTROL/errormast
