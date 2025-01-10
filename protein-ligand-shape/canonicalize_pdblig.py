"""Canonicalize the order of atoms in the input PDB file containing a ligand."""

import sys
import string
from pathlib import Path
from rdkit import Chem


__dev__ = "Victor G.P. Reys"


def renumber(pdbblock):
    renumbered = ""
    countings = {}
    # Loop over lines
    for _ in pdbblock.split("\n"):
        # If ATOM/HETATM record
        if _.startswith(("ATOM", "HETATM", )):
            # Capture current atom name
            atomname = _[12:16]
            attype = "".join([l for l in atomname if l in string.ascii_uppercase])
            # Increment counting
            count = countings.setdefault(attype, 0)
            count += 1
            countings[attype] = count
            # Set new atom name based on counts
            new_atname = f"{attype}{count}"
            # Re-build the line
            new_ = f"{_[:12]}{new_atname:^4s}{_[16:]}\n"
            # Hold it
            renumbered += new_
        # Do not keep CONECT records
        elif _.startswith(("CONECT", )):
            continue
        else:
            renumbered += _ + "\n"
    return renumbered


def reorder(fname):
    reference = Chem.MolFromPDBFile(fname)
    # NOTE: must run MolToSmiles to have access to "_smilesAtomOutputOrder"
    _smi = Chem.MolToSmiles(reference)
    # get the atoms in the smiles string order
    order = reference.GetPropsAsDict(True,True)["_smilesAtomOutputOrder"]
    # Re-order based on SMILES ordering
    ref_canonical = Chem.RenumberAtoms(reference, order)
    # Generate a PDB block
    newref_block = Chem.MolToPDBBlock(ref_canonical)
    return newref_block


def main(fname):
    # Canonicalise the order of atoms
    newref_block = reorder(fname)
    # Renumber atoms
    renumbered = renumber(newref_block)
    # Write canonical version of the ligand
    input_path = Path(fname)
    newpath = Path(input_path.parent.resolve(), f"canonical_{input_path.name}")
    newpath.write_text(renumbered)


def maincli():
    try:
        fname = sys.argv[1]
    except IndexError:
        exit("Usage:\npython3 canonicalize_pdblig.py <path/to/ligand.pdb>")
    main(fname)


if __name__ == "__main__":
    maincli()
