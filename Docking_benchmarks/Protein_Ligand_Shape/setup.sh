#!/usr/bin/env bash
#
# setup.sh — prepare protein–ligand-shape benchmark for haddock-runner 3.0.0.
# Idempotent. Requires: python3, pdb_mkensemble, curl.

set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "[1/5] Converting HADDOCK2 inputs to HADDOCK3..."
python3 haddock2_to_haddock3.py

echo "[2/5] Canonicalizing reference ligands..."
for d in references/*/; do
    t="$(basename "$d")"
    for src in "${d}${t}_ref.pdb" "${d}${t}_ligref.pdb"; do
        dst="${src%.pdb}_can.pdb"
        [ -f "$src" ] && [ ! -f "$dst" ] && python3 canonicalize_pdblig.py "$src"
    done
done

echo "[3/5] Building ligand ensembles..."
for d in conformers/*/; do
    t="$(basename "$d")"; cd "$d"
    files=( "${t}"_l_u_[0-9]*.pdb )
    if [ "${#files[@]}" -gt 1 ] && [ ! -f "${t}_l_u.pdb" ]; then
        pdb_mkensemble "${files[@]}" > "${t}_l_u.pdb"
        mkdir -p _conformers_orig && mv "${files[@]}" _conformers_orig/
    fi
    cd "$ROOT"
done

echo "[4/5] Updating input_list.txt with ensemble paths..."
cp input_list.txt input_list.txt.bak
grep -vE '_l_u_[0-9]+\.pdb$' input_list.txt.bak > input_list.txt
for d in conformers/*/; do
    t="$(basename "$d")"
    ens="${ROOT}/conformers/${t}/${t}_l_u.pdb"
    grep -qF "$ens" input_list.txt || echo "$ens" >> input_list.txt
done

echo "[5/5] Downloading AnalyseBenchmarkResults.py..."
curl -sSL https://raw.githubusercontent.com/haddocking/haddock-tools/refs/heads/master/AnalyseBenchmarkResults.py -o AnalyseBenchmarkResults.py

echo "Done."
