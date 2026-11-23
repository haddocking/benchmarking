#!/bin/bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/scripts/_common.sh"

# Download the nanobody-antigen dataset, converging to the pinned commit
clone_pinned https://github.com/haddocking/nanobodies.git nanobody-antigen-dataset "$NANOBODIES_REF"

# Create input list: the IBMu nanobody ensemble, the unbound antigen, the
#  reference, and the restraint files of each information scenario
ls $(pwd)/nanobody-antigen-dataset/benchmark_pdb_files/*/*.{pdb,tbl} |
  grep -E "_af_multi_imbuilder_ensemble\.pdb$|_l_u\.pdb$|_ref\.pdb$|_(real|loose|twohit|allsurface)_ambig\.tbl$|_l_u_unambig\.tbl$" |
  sort >nanobody-antigen-input.txt
