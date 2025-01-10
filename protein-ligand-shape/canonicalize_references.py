from pathlib import Path
from canonicalize_pdblig import main as canonicalize_pdblig


def replace_in_ref(canonical, original):
    original_fpath = Path(original)
    canonical_ref = Path(original_fpath.parent.resolve(), f"{original_fpath.stem}_can.pdb")
    with open(original, "r") as fin, open(canonical_ref, "w") as filout, open(canonical, "r") as canlig:
        for _ in fin:
            if _.startswith(("ATOM", "HETATM", )):
                if _[17:20] != "UNK":
                    filout.write(_)
            elif _.startswith("TER"):
                filout.write(_)
        for lig_ in canlig:
            filout.write(lig_)


def main():
    # Loop over all targets
    for dirname in Path("references").glob("*"):
        tname = dirname.stem
        # Search for ligand alone
        ligand_pdb_fpath = f"{dirname}/{tname}_ligref.pdb"
        # Canonicalise it
        canonical_lig = canonicalize_pdblig(ligand_pdb_fpath)
        # Add file content in ref.pdb
        replace_in_ref(canonical_lig, f"{dirname}/{tname}_ref.pdb")


if __name__ == "__main__":
    main()

