#!/bin/bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/scripts/_common.sh"

# Download and extract protein-peptide dataset, converging to the pinned commit
clone_pinned https://github.com/haddocking/protein-peptide protein-peptide-dataset "$PROTEIN_PEPTIDE_REF"

ls $(pwd)/protein-peptide-dataset/**/*.{pdb,tbl} |
  grep -v "ana_scripts\|matched\|cg" |
  grep -E "_r_u\.pdb$|_l_u\.pdb$|_r_b\.pdb$|_l_b\.pdb$|_b_ambig\.tbl$|_target\.pdb$" |
  sort >protein-peptide-input.txt

# The unbound scenarios: only the complexes with an unbound receptor, with the
#  restraints of the unbound structures
for id in $(cat protein-peptide-dataset/unbound-complexes.txt); do
  for f in ${id}_r_u.pdb ${id}_l_u.pdb ${id}_u_ambig.tbl ${id}_target.pdb; do
    echo "$(pwd)/protein-peptide-dataset/${id}/${f}"
  done
done >protein-peptide-input-unbound.txt
