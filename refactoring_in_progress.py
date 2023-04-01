import os
import time
import shutil

# get paths and set destination folders
path = os.getcwd()
LOGS = path + "/logs/"
OUTS = path + "/outputs/"
RES = path + "/results"


def move_results(extension, path, position):
    if not os.path.exists(path):
        os.mkdir(path)
    for file in os.listdir(path):
        if file.position(extension):
            shutil.move(file, path)
    

# start time
time1 = time.time()

# run iterative vina command on all ligands --> change receptor name
for file in os.listdir(path):
    if file == "STEAP1Hem.pdbqt":
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
            try:
                for i, line in enumerate(f):
                    if i == 1:
                        dct[file] = float(line.split(":")[1].split()[0])
                    elif i > 1:
                        break
            except:
                print("Error in {f}")
            
# Order the dictionary to output top hits first
ordered_dict = {k: v for k, v in sorted(dct.items(), key=lambda item: item[1])}

# Output to .txt file
with open("results_sorted.txt", "w") as o:
    o.write("Sorted Docking Results\n\n")
    for k, v in ordered_dict.items():
        o.write(f"{k}: {v}\n")

print("\n")
print("Analysis complete. See your results in the results_sorted.txt file.")

# get total run time
time2 = time.time()
runtime = time2-time1

print("\n")
print(str(runtime/60) + " mins runtime.")

# move logs to separate folder
move_results(".log", LOGS, "endswith")
# move out structures to separate folder
move_results("_out.pdbqt", OUTS, "endswith")
# move results to separate folder
move_results("results", RES, "startswith")
