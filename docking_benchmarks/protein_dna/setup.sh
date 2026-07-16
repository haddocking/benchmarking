#!/bin/bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/scripts/_common.sh"

# pdb_mkensemble comes from pdb-tools, installed in the repo's .venv.
export PATH="$VENV_PATH/bin:$PATH"

# Download benchmark if it does not already exist, then converge to the pinned commit
clone_pinned https://github.com/haddocking/Prot-DNABenchmark protein-dna "$PROT_DNA_BENCHMARK_REF"

# Check that pdb_mkensemble is available
if ! command -v pdb_mkensemble >/dev/null 2>&1; then
  echo "Error: pdb_mkensemble not found."
  echo "Run setup.sh (repo root) first to create the .venv (which installs pdb-tools)."
  exit 1
fi

echo "Creating ensemble files..."

for dir in protein-dna/*/; do
  case=$(basename "$dir")

  for base in $(
    ls "$dir" |
      grep -E "${case}_p[0-9]+_u_[0-9]+\.pdb$" |
      sed 's/_[0-9]*\.pdb$//' |
      sort -u
  ); do
    outfile="${dir}/${base}.pdb"

    if [ ! -f "$outfile" ]; then
      echo "Creating $outfile"
      pdb_mkensemble "${dir}/${base}"_*.pdb >"$outfile"
    fi
  done
done

echo "Generating input list..."

find "$(pwd)/protein-dna" \
  \( -name "*.pdb" -o -name "*.tbl" \) |
  grep -E "_p[0-9]+_u\.pdb$|_p[0-9]+_b\.pdb$|_d_u\.pdb$|_d_b\.pdb$|_u_ambig\.tbl$|_b_ambig\.tbl$|_target\.pdb$" |
  sort >prot-dna-input.txt
