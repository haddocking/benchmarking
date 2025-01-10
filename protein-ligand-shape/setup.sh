# Download benchmark and make it haddock3 haddock-runner ready
python3 haddock2_to_haddock3.py
python3 canonicalize_references.py
# Copy a subset of the input list for testing
cat input_list.txt | grep "/ppar" > input_list_ppar.txt
# Download the Analysis script
curl https://raw.githubusercontent.com/haddocking/haddock-tools/refs/heads/master/AnalyseBenchmarkResults.py > AnalyseBenchmarkResults.py 
