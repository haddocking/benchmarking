#!/usr/bin/env bash
#
# setup.sh — prepare protein–ligand-shape benchmark for haddock-runner 3.0.0.
# Idempotent. Requires: python3, pdb_mkensemble.

set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

# python3/rdkit and pdb_mkensemble come from the repo's .venv.
REPO_ROOT="$(cd "$ROOT/../.." && pwd)"
export PATH="$REPO_ROOT/.venv/bin:$PATH"

# Rewrite HADDOCK2-style topology/parameter references to HADDOCK3 format
echo "[1/4] Converting HADDOCK2 inputs to HADDOCK3..."
python3 haddock2_to_haddock3.py

# Produce a canonicalized ligand PDB (_can.pdb) for each reference structure;
# skipped if the output already exists
echo "[2/4] Canonicalizing reference ligands..."
for d in references/*/; do
    t="$(basename "$d")"
    for src in "${d}${t}_ref.pdb" "${d}${t}_ligref.pdb"; do
        dst="${src%.pdb}_can.pdb"
        [ -f "$src" ] && [ ! -f "$dst" ] && python3 canonicalize_pdblig.py "$src"
    done
done

# Merge per-conformer PDBs (e.g. 1ABC_l_u_1.pdb, _2.pdb …) into a single
# multi-model ensemble file; originals are archived into _conformers_orig/
echo "[3/4] Building ligand ensembles..."
for d in conformers/*/; do
    t="$(basename "$d")"; cd "$d"
    files=( "${t}"_l_u_[0-9]*.pdb )
    if [ "${#files[@]}" -gt 1 ] && [ ! -f "${t}_l_u.pdb" ]; then
        pdb_mkensemble "${files[@]}" > "${t}_l_u.pdb"
        mkdir -p _conformers_orig && mv "${files[@]}" _conformers_orig/
    fi
    cd "$ROOT"
done

# Replace individual conformer entries with ensemble paths
echo "[4/4] Updating protein-ligand-shape-input.txt with ensemble paths..."
tmp=$(mktemp)
grep -vE '_l_u_[0-9]+\.pdb$' protein-ligand-shape-input.txt > "$tmp"
mv "$tmp" protein-ligand-shape-input.txt
for d in conformers/*/; do
    t="$(basename "$d")"
    ens="${ROOT}/conformers/${t}/${t}_l_u.pdb"
    grep -qF "$ens" protein-ligand-shape-input.txt || echo "$ens" >> protein-ligand-shape-input.txt
done

echo "Done."
