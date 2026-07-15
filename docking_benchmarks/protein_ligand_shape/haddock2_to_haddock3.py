"""Preprocess the ligand-shape haddocking benchmark set to fit haddock-runner.

Usage:
python3 haddock2_to_haddock3.py
"""

import os
import shutil

from pathlib import Path
from canonicalize_pdblig import main as canonicalize_pdblig


SHAPE_ROOT = "./shape-restrained-haddocking/"


def list_dirs(path: str):
    return Path(path).glob("*")


def conformers():
    conformers_dirpath = Path("conformers")
    conformers_dirpath.mkdir(exist_ok=True)
    for target_path in list_dirs(SHAPE_ROOT + "conformers/"):
        target = target_path.stem
        new_target_path = Path(conformers_dirpath, target)
        new_target_path.mkdir(exist_ok=True)
        for conformer in target_path.glob("*.pdb"):
            conf_id = int(conformer.stem.split("_")[-1])
            new_conformer_path = Path(new_target_path, f"{target}_l_u_{conf_id}.pdb")
            shutil.copyfile(conformer, new_conformer_path)
            correct_chainid(new_conformer_path, "B")


def smiles():
    smiles_dirpath = Path("smiles")
    smiles_dirpath.mkdir(exist_ok=True)
    for target_path in list_dirs(SHAPE_ROOT + "conformers/"):
        target = target_path.stem
        for smi in target_path.glob("*.smi"):
            new_conformer_path = Path(smiles_dirpath, f"{target}_ligand.smi")
            shutil.copyfile(smi, new_conformer_path)


def restraints():
    restraints_dirpath = Path("restraints")
    restraints_dirpath.mkdir(exist_ok=True)

    for rest_type_path in list_dirs(SHAPE_ROOT + "restraints/"):
        rest_type = rest_type_path.stem
        restraints_type_dirpath = Path(restraints_dirpath, rest_type)
        restraints_type_dirpath.mkdir(exist_ok=True)

        for target_restraints_path in list_dirs(f"{rest_type_path}/"):
            target = target_restraints_path.stem
            new_target_path = Path(restraints_type_dirpath, target)
            new_target_path.mkdir(exist_ok=True)

            for tbl in target_restraints_path.glob("*.tbl"):
                if "ambig" in str(tbl):
                    suffix = "unambig" if "unambig" in str(tbl) else "ambig"
                else:
                    suffix = tbl.stem
                    if "low_sim_unbound" in suffix:
                        suffix = suffix.replace("unbound", "unb")
                new_tbl_path = Path(new_target_path, f"{target}_{suffix}.tbl")
                shutil.copyfile(tbl, new_tbl_path)


def shapes():
    shapes_dirpath = Path("shapes")
    shapes_dirpath.mkdir(exist_ok=True)

    for shapes_type_path in list_dirs(SHAPE_ROOT + "shapes/"):
        shapes_type = shapes_type_path.stem

        for target_shapes_path in list_dirs(f"{shapes_type_path}/"):
            target = target_shapes_path.stem

            for pdb_shape in target_shapes_path.glob("*.pdb"):
                new_tbl_path = Path(shapes_dirpath, f"{target}_{shapes_type}_beads.pdb")
                shutil.copyfile(pdb_shape, new_tbl_path)


def references():
    references_dirpath = Path("references")
    references_dirpath.mkdir(exist_ok=True)

    for target_path in list_dirs(SHAPE_ROOT + "structures/"):
        target = target_path.stem
        new_target_path = Path(references_dirpath, target)
        new_target_path.mkdir(exist_ok=True)

        for fname, suffix in zip(
            (
                "bound.pdb",
                "bound_ligand.pdb",
            ),
            (
                "ref",
                "ligref",
            ),
        ):
            fpath = Path(target_path, fname)
            new_conformer_path = Path(new_target_path, f"{target}_{suffix}.pdb")
            shutil.copyfile(fpath, new_conformer_path)

        # Search for ligand alone
        ligand_pdb_fpath = Path(new_target_path, f"{target}_ligref.pdb")
        # Canonicalise it
        canonical_lig = canonicalize_pdblig(ligand_pdb_fpath.resolve())
        # Add file content in ref.pdb
        replace_in_ref(canonical_lig, f"{new_target_path}/{target}_ref.pdb")


def replace_in_ref(canonical, original):
    original_fpath = Path(original)
    canonical_ref = Path(
        original_fpath.parent.resolve(), f"{original_fpath.stem}_can.pdb"
    )
    with (
        open(original, "r") as fin,
        open(canonical_ref, "w") as filout,
        open(canonical, "r") as canlig,
    ):
        for _ in fin:
            if _.startswith(
                (
                    "ATOM",
                    "HETATM",
                )
            ):
                if _[17:20] != "UNK":
                    filout.write(_)
            elif _.startswith("TER"):
                filout.write(_)
        for lig_ in canlig:
            filout.write(lig_.replace("HETATM", "ATOM  "))


def receptors():
    recept_dirpath = Path("receptors")
    recept_dirpath.mkdir(exist_ok=True)

    for recept_type_path in list_dirs(SHAPE_ROOT + "templates/"):
        recept_type = recept_type_path.stem
        recept_type_dirpath = Path(recept_dirpath, recept_type)
        recept_type_dirpath.mkdir(exist_ok=True)

        for target_recept_path in list_dirs(f"{recept_type_path}/"):
            target = target_recept_path.stem
            new_target_path = Path(recept_type_dirpath, target)
            new_target_path.mkdir(exist_ok=True)

            for pdb in target_recept_path.glob("*unbound.pdb"):
                new_rec_path = Path(new_target_path, f"{target}_r_u_{recept_type}.pdb")
                shutil.copyfile(pdb, new_rec_path)
                correct_chainid(new_rec_path, "A")


def correct_chainid(pdbpath, chainid):
    with open(pdbpath, "r") as filin:
        filedt = filin.readlines()
    with open(pdbpath, "w") as fout:
        for _ in filedt:
            if _.startswith(
                (
                    "ATOM",
                    "HETATM",
                )
            ):
                n_ = _[:21] + chainid[0] + _[22:]
                fout.write(n_)
            else:
                fout.write(_)


def toppars():
    toppar_dirpath = Path("toppars")
    toppar_dirpath.mkdir(exist_ok=True)

    for target_toppar_path in list_dirs(SHAPE_ROOT + "toppar/"):
        target = target_toppar_path.stem

        for fname in (
            "ligand.param",
            "ligand.top",
        ):
            fpath = Path(target_toppar_path, fname)
            new_f_path = Path(toppar_dirpath, f"{target}_{fname}")
            shutil.copyfile(fpath, new_f_path)


def check_dataset():
    repo_dir = Path(SHAPE_ROOT)
    if not repo_dir.exists():
        raise SystemExit(
            f"{repo_dir} not found. setup.sh should have cloned it - run "
            "setup.sh instead of this script directly."
        )


def gen_input_mapper():
    dirs_to_gather = (
        "conformers",
        "receptors",
        "references",
        "restraints",
        "shapes",
        "toppars",
    )
    with open("protein-ligand-shape-input.txt", "w") as filout:
        for d in dirs_to_gather:
            filout.write(f"# {d.upper()}\n")
            for fpath in all_files(d):
                filout.write(f"{fpath.resolve()}\n")


def all_files(dirname: str):
    for path, _subdirs, files in os.walk(dirname):
        for name in files:
            yield Path(path, name)


def to_haddock_runner():
    conformers()  # input ligands
    toppars()  # input ligands topologies and parameters
    restraints()  # input restraints
    shapes()  # input shapes
    receptors()  # input receptors/protiens
    references()  # xray reference structures
    smiles()  # ligand smiles


def main():
    # Dataset is cloned by setup.sh before this script runs
    check_dataset()

    # Make it haddock-runner / haddock3 ready
    to_haddock_runner()

    # Generate input file
    gen_input_mapper()


def runmain():
    initdir = os.getcwd()
    os.chdir(Path(__file__).resolve().parent)
    main()
    os.chdir(initdir)


if __name__ == "__main__":
    runmain()
