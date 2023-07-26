from rdkit import Chem

def set_id_as_title(input_file, output_file):
    # Read the SDF file using RDKit
    suppl = Chem.SDMolSupplier(input_file)

    # Initialize a list to store modified molecules
    modified_molecules = []

    for mol in suppl:
        if mol is None:
            continue

        # Get the <ID> value
        mol_id = mol.GetProp('Catalog ID')

        # Set the <ID> as the title for the molecule
        mol.SetProp('_Name', mol_id)

        # Append the modified molecule to the list
        modified_molecules.append(mol)

    # Write the modified molecules to a new SDF file
    writer = Chem.SDWriter(output_file)
    for mol in modified_molecules:
        writer.write(mol)
    writer.close()

if __name__ == '__main__':
    input_sdf_file = 'Enamine_Discovery_Diversity_Set_10240cmpds_20221105.sdf'
    output_sdf_file = 'output_with_title.sdf'
    set_id_as_title(input_sdf_file, output_sdf_file)
