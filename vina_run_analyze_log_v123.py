import os
import time

time1 = time.time()

# get path
path = os.getcwd()

# run iterative vina command on all ligands --> change receptor name
for file in os.listdir(path):
    if file == "receptor.pdbqt":
        continue
    elif file.endswith(".pdbqt"):
        # call vina
        cmd = f"vina --config conf.txt --ligand {file}"
        output = os.popen(cmd).read()
        # display ligand output in terminal 
        print(output)
        # dump to log file
        with open(f"{file}_log.log", "w") as log:
            log.write(output)

# create results.txt with all num_modes for all ligands
os.system("tail -n14 *.log > results.txt")


print("\n")
print("Starting analysis...")
dct = {}

# iterate over log files and output results in dict form
for file in os.listdir(path):
    if file.endswith("out.pdbqt"):
        with open(file, "r") as f:
            for i, line in enumerate(f):
                if i == 1:
                    dct[file] = float(line.split(":")[1].split()[0])
                elif i > 1:
                    break

# Order the dictionary to output top hits first
ordered_dict = {k: v for k, v in sorted(dct.items(), key=lambda item: item[1])}

# Output to .txt file
with open("results_sorted.txt", "w") as o:
    o.write("Sorted Docking Results\n\n")
    for k, v in ordered_dict.items():
        o.write(f"{k}: {v}\n")

print("\n")
print("Analysis complete. See your results in the results_sorted.txt file.")

time2 = time.time()

print("\n")
print(time2 - time1)
