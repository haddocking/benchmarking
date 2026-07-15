#!/bin/bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/scripts/_common.sh"

# Download and extract protein-peptide dataset, converging to the pinned commit
clone_pinned https://github.com/haddocking/protein-peptide protein-peptide-dataset "$PROTEIN_PEPTIDE_REF"

ls $(pwd)/protein-peptide-dataset/**/*.{pdb,tbl} |
  grep -v "ana_scripts\|matched\|cg" |
  grep -E "_r_u\.pdb$|_l_u\.pdb$|_b_ambig\.tbl$|_target\.pdb$" |
  sort >protein-peptide-input.txt
