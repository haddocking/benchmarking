#!/bin/bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/scripts/_common.sh"

# Download the protein-glycans dataset, converging to the pinned commit
clone_pinned https://github.com/haddocking/protein-glycans.git protein-glycan-dataset "$PROTEIN_GLYCANS_REF"

# Create a `input-files.txt` file
ls $(pwd)/protein-glycan-dataset/pdb_files/**/*.{pdb,tbl} | grep -v "ana_scripts\|matched\|cg" | sort >protein-glycan-input.txt

# The unbound scenarios: only the complexes with an unbound receptor and a
#  glycan ensemble
for dir in protein-glycan-dataset/pdb_files/*/; do
  id=$(basename "$dir")
  [ -e "$dir/${id}_r_u.pdb" ] && [ -e "$dir/${id}_l_ensemble.pdb" ] || continue
  for f in ${id}_r_u.pdb ${id}_l_ensemble.pdb ${id}_tip-ap.tbl ${id}_analysis.pdb; do
    echo "$(pwd)/protein-glycan-dataset/pdb_files/${id}/${f}"
  done
done >protein-glycan-input-unbound.txt
