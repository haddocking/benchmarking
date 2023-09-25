#!/bin/bash
#===============================================================================
#
# Setup script for the project
#
#===============================================================================

# Configure Python Environment
echo "Configuring Python Environment with Anaconda"
conda create -n haddock3-benchmark python=3.9 || exit
conda activate haddock3-benchmark

# Install HADDOCK3
echo "Installing HADDOCK3"
git clone --recursive https://github.com/haddocking/haddock3.git
cd haddock3
cd src/fcc/src
chmod u+x Makefile
make
cd -
pip install -r requirements.txt
python setup.py develop

echo "Get the CNS binary"
mkdir -p bin/
curl https://surfdrive.surf.nl/files/index.php/s/f2Iy0Zg1xObSA69/download -o bin/cns
chmod +x bin/cns