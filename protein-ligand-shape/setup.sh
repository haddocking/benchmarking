# Download benchmark and make it haddock3 haddock-runner ready
python3 haddock2_to_haddock3.py
# Copy a subset of the input list for testing
cat input_list.txt | grep "/ppar" > input_list_ppar.txt
# Modify paths in input list(s)
find . -type f -name "*.yml" -exec sed -i "s|_ABSPATH_PWD_|$PWD|g" {} +
