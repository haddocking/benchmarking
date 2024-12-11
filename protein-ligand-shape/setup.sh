# Download benchmark and make it haddock3 haddock-runner ready
python3 haddock2_to_haddock3.py
# Copy a subset of the input list for testing
cat input_list.txt | grep "/ppar" > input_list_small.txt
# Modify paths in input list(s)
sed -i "s/_ABSPATH_PWD_/$PWD/g" benchmark-unbound-unbound.yml
sed -i "s/_ABSPATH_PWD_/$PWD/g" benchmark-unbound-unbound-small.yml
