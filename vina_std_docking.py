import os
import time
import shutil
import subprocess
import logging
import argparse
from contextlib import suppress


# Constants
PATH = os.getcwd()
LOGS = PATH + "/logs/"
OUTS = PATH + "/outputs/"
RES = PATH + "/results"
BACKUP = PATH + "/backup/"
INPUTS = PATH + "/inputs/"


def setup_logging():
    """Set up logging to both a file and the console.

    The logging is configured to log messages with a timestamp, log level, and message content.
    It creates two handlers: one to log messages to a file named 'docking_log.txt' and another to log messages to the console.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler("docking_log.txt"), logging.StreamHandler()]
    )


def move_results(extension, path, position):
    """Make storage and move files with startswith/endswith extension.

    Args:
        extension (str): File extension to move.
        path (str): Destination path to move files.
        position (str): Either 'startswith' or 'endswith' to specify how to match the file names.

    Raises:
        shutil.Error: If there's an error while moving the files.

    """
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        for file in os.listdir(os.getcwd()):
            if getattr(file, position)(extension) and file != RECEPTOR_FILE:
                with suppress(shutil.Error):
                    shutil.move(file, path)
    except Exception as err:
        logging.error(f"Error moving files: {err}")


def run_subprocess(cmd):
    """Run an external command and return the output.

    Args:
        cmd (str): The command to be executed.

    Returns:
        str: The standard output of the command.

    Raises:
        subprocess.CalledProcessError: If the command returns a non-zero exit code.

    """
    try:
        completed_process = subprocess.run(cmd, shell=True, text=True, capture_output=True, check=True)
        return completed_process.stdout
    except subprocess.CalledProcessError as err:
        logging.error(f"Error executing command: {err.stderr}")
        return ""


def convert_sdf_to_pdbqt():
    """Add protonation state to conformers (default pH 7.4) and convert SDF to PDBQT using obabel.

    The function executes OpenBabel commands to convert the input SDF files to PDBQT format.
    It adds protonation state to the conformers at pH 7.4 before converting.
    """
    os.system("obabel conformers.sdf -O prep_subs.sdf -p --unique cansmiNS")
    os.system("obabel -isdf prep_subs.sdf -osdf -O *.sdf --split --unique")
    os.system("obabel -isdf *.sdf -opdbqt -O*.pdbqt")


def remove_blank_pdbqt_files():
    """Remove blank pdbqt files generated during the conversion.

    The function removes temporary PDBQT files ('prep_subs.pdbqt' and 'conformers.pdbqt') created during the conversion process.
    """
    for file in ["prep_subs.pdbqt", "conformers.pdbqt"]:
        try:
            os.remove(file)
        except FileNotFoundError:
            pass


def run_vina_on_ligands():
    """Run Vina for each ligand (excluding the receptor).

    The function executes Vina commands for each ligand (PDBQT files) found in the current working directory.
    It skips the receptor file specified as a command-line argument.
    The function prints the output of each Vina run to the console and saves it to log files.
    """
    for file in os.listdir(PATH):
        if file == RECEPTOR_FILE:
            continue
        elif file.endswith(".pdbqt"):
            # Call Vina
            cmd = f"vina --config {CONFIG_FILE} --ligand {file}"
            output = run_subprocess(cmd)
            # Display ligand output in terminal
            print(output)
            # Dump to log file
            with open(f"{file}_log.log", "w", encoding="utf-8") as log:
                log.write(output)


def extract_and_sort_results():
    """Extract scores from log files and create a sorted results.txt file.

    The function extracts docking scores from log files generated during Vina runs.
    It creates a sorted 'results.txt' file based on the scores, displaying the top hits first.
    """
    os.system("tail -n14 *.log > results.txt")
    
    print("\n")
    print("Starting analysis...")
    dct = {}

    for file in os.listdir(PATH):
        if file.endswith("out.pdbqt"):
            with open(file, "r", encoding="utf-8") as f:
                try:
                    for i, line in enumerate(f):
                        if i == 1:
                            dct[file] = float(line.split(":")[1].split()[0])
                            break
                except:
                    logging.error(f"Error processing {file}")

    # Order the dictionary to output top hits first
    ordered_dict = {k: v for k, v in sorted(dct.items(), key=lambda item: item[1])}

    # Output to .txt file
    with open("results_sorted.txt", "w", encoding="utf-8") as out:
        out.write("Sorted Docking Results\n\n")
        for k, v in ordered_dict.items():
            out.write(f"{k}: {v}\n")

    print("\n")
    print("Analysis complete. See your results in the results_sorted.txt file.")


def main():
    """Main"""
    setup_logging()

    # Convert SDF to PDBQT and remove blank pdbqt files
    convert_sdf_to_pdbqt()
    remove_blank_pdbqt_files()

    # Start time for docking
    time1 = time.time()

    # move sdfs to backup
    move_results(".sdf", BACKUP, "endswith")
    
    # Run Vina on ligands
    run_vina_on_ligands()

    # Extract and sort results
    extract_and_sort_results()

    # Get total run time
    time2 = time.time()
    runtime = time2 - time1

    # Display runtime in minutes
    print("\n")
    print(str(runtime / 60) + " mins runtime.")

    # move logs to separate folder
    move_results(".log", LOGS, "endswith")
    # move docked structures to output folder
    move_results("_out.pdbqt", OUTS, "endswith")
    # move .pdbqt to inputs folder
    move_results(".pdbqt", INPUTS, "endswith")
    # Move results to results folder
    move_results("results", RES, "startswith")


if __name__ == "__main__":
    # Set up argparse to handle command-line arguments
    parser = argparse.ArgumentParser(description="Script for Vina Standard Docking")
    parser.add_argument(
        "--receptor",
        required=True,
        type=str,
        help="Name of receptor file in PDBQT format. This file represents the target protein for docking.",
    )
    parser.add_argument(
        "--config",
        required=True,
        type=str,
        help="Name of configuration file. This file contains the parameters and settings for the Vina docking process.",
    )
    args = parser.parse_args()

    # Bind args values to global variables
    RECEPTOR_FILE = args.receptor
    CONFIG_FILE = args.config

    # Call the main function
    main()
