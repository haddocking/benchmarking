#!/bin/bash

# Download protein-DNA benchmark dataset
git clone https://github.com/haddocking/Prot-DNABenchmark
mv Prot-DNABenchmark protein-dna

# Merge NMR ensemble models back into single files for HADDOCK
# e.g. 1HJC_p1_u_1.pdb + 1HJC_p1_u_2.pdb → 1HJC_p1_u.pdb
for dir in protein-dna/*/; do
    case=$(basename $dir)
    for base in $(ls $dir | grep -E "${case}_p[0-9]+_u_[0-9]+\.pdb$" | sed 's/_[0-9]*\.pdb$//' | sort -u); do
        outfile="$dir/${base}.pdb"
        if [ ! -f "$outfile" ]; then
            cat $dir/${base}_*.pdb > "$outfile"
            echo "Merged ensemble: $outfile"
        fi
    done
done

# One flat input list — scenarios are defined in benchmark.yaml
# Includes all file types needed across all three scenarios
ls $(pwd)/protein-dna/**/*.{pdb,tbl} \
  | grep -E "_p[0-9]+_u\.pdb$|_p[0-9]+_b\.pdb$|_d_u\.pdb$|_d_b\.pdb$|_u_ambig\.tbl$|_b_ambig\.tbl$|_target\.pdb$" \
  | sort > protein-dna-input.txt
