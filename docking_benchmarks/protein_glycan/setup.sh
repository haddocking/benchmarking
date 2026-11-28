#!/bin/bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/scripts/_common.sh"

# pdb_mkensemble comes from pdb-tools, installed in the repo's .venv.
export PATH="$VENV_PATH/bin:$PATH"

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
done | sort >protein-glycan-input-unbound.txt

# The flexdock scenario pairs receptor and glycan models one to one: build a
#  receptor ensemble with as many copies of the unbound receptor as the
#  glycan ensemble has models
while read -r f; do
  case "$f" in *_r_u.pdb) ;; *) continue ;; esac
  ens="${f%.pdb}_ensemble.pdb"
  if [ ! -f "$ens" ]; then
    n=$(grep -c '^MODEL' "${f%_r_u.pdb}_l_ensemble.pdb")
    pdb_mkensemble $(for i in $(seq "$n"); do echo "$f"; done) >"$ens"
  fi
done <protein-glycan-input-unbound.txt
sed 's/_r_u\.pdb$/_r_u_ensemble.pdb/' protein-glycan-input-unbound.txt >protein-glycan-input-flexdock.txt
