#!/bin/bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/scripts/_common.sh"

# Download the protein-glycans dataset, converging to the pinned commit
clone_pinned https://github.com/haddocking/protein-glycans.git protein-glycan-dataset "$PROTEIN_GLYCANS_REF"

# Create a `input-files.txt` file
ls $(pwd)/protein-glycan-dataset/pdb_files/**/*.{pdb,tbl} | grep -v "ana_scripts\|matched\|cg" | sort >protein-glycan-input.txt
