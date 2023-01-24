# Vina-VS-Docking-Script

### Run Virtual Screening on a set of pdbqt ligands and outputs a results_sorted.txt file with sorted hits.

Call it as a standard python script:
`python3 merge_run_analyze.py` within the working directory.

The script outputs a results.txt with all binding affinities (assuming a num_modes = 10) for all ligands.

Also grabs the best binding affinity energy for each ligand and outputs in a sorted format in the results_sorted.txt.

Don't forget to change the receptor name in `receptor.pdbqt` for your protein file name.

