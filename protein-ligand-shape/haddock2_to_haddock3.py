"""Preprocess the ligand-shape haddocking benchmark set to fit haddock-runner.

Usage:
python3 haddock2_to_haddock3.py
"""

import os
import shutil
import subprocess

from pathlib import Path

LIGAND_SHAPE_GIT_REPO_URL = "https://github.com/haddocking/shape-restrained-haddocking.git"
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

        for fname, suffix in zip(("bound.pdb", "bound_ligand.pdb", ), ("ref", "ligref", )):
            fpath = Path(target_path, fname)
            new_conformer_path = Path(new_target_path, f"{target}_{suffix}.pdb")
            shutil.copyfile(fpath, new_conformer_path)


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
                new_rec_path = Path(new_target_path, f"{target}_r_u.pdb")
                shutil.copyfile(pdb, new_rec_path)


def toppars():
    toppar_dirpath = Path("toppars")
    toppar_dirpath.mkdir(exist_ok=True)

    for target_toppar_path in list_dirs(SHAPE_ROOT + "toppar/"):
        target = target_toppar_path.stem

        for fname in ("ligand.param", "ligand.top", ):
            fpath = Path(target_toppar_path, fname)
            new_f_path = Path(toppar_dirpath, f"{target}_{fname}")
            shutil.copyfile(fpath, new_f_path)


def download_dataset():
    repo_dir = Path(SHAPE_ROOT)
    if repo_dir.exists():
        return
    
    git_clone = subprocess.Popen(
        ["git", "clone", LIGAND_SHAPE_GIT_REPO_URL],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        )
    _output = git_clone.stdout.read()
    assert repo_dir.exists()


def gen_input_mapper():
    dirs_to_gather = (
        "conformers",
        "receptors",
        "references",
        "restraints",
        "shapes",
        "toppars",
        )
    with open("input_list.txt", "w") as filout:
        for d in dirs_to_gather:
            filout.write(f"# {d.upper()}\n")
            for fpath in all_files(d):
                filout.write(f"{fpath.resolve()}\n")


def smaller_set():
    subprocess.run(
        'cat input_list.txt | grep "/ppar" > input_list_ppar.txt',
        shell=True,
        )


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
    # Download the input dataset
    download_dataset()

    # Make it haddock-runner / haddock3 ready
    to_haddock_runner()

    # Generate input file
    gen_input_mapper()

    # Generate smaller set
    smaller_set()
    

def runmain():
    initdir = os.getcwd()
    os.chdir(Path(__file__).resolve().parent)
    main()
    os.chdir(initdir)


if __name__ == "__main__":
    runmain()
