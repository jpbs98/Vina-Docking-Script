import pandas as pd
import os

# Load the data into a DataFrame, skipping the first 5 lines
df = pd.read_csv("./ChemPLP-Docking//bestranking_changes.lst", skiprows=5, delim_whitespace=True, index_col=False, quotechar="'")

# Drop the two columns with NaN values
df.drop(columns=["Ligand", "name.1"], inplace=True)

df['File'] = df['File'].str.replace(r'^\.\x5C', '', regex=True)

if not os.path.exists("./mv_ligs_for_rescore"):
    os.mkdir("./mv_ligs_for_rescore")

for lig in df["File"]:
    os.system(f"cp ./ChemPLP-Docking/{lig} ./mv_ligs_for_rescore/")