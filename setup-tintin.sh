#!/bin/bash
#===============================================================================
#
# Setup script for the project
#
#===============================================================================

export PYTHON_VERSION=3.9.18
export VENV_NAME=.venv

# Explain what the script does and wait for confirmation
echo "[+] This script will setup the project"
echo "[+] It will install the following packages:"
echo "[+]     - pyenv in your HOME directory"
echo "[+]     - python ${PYTHON_VERSION} in your HOME directory"
echo "[+]     - virtual environment ${VENV_NAME} in the current directory"
echo "[+]     - HADDOCK3 in the virtual environment"
echo "[+]     - Download the haddock-runner"
echo "[+]"
echo "[!!] This will NOT USE ANACONDA/MINICONDA"
echo "[!!] All installations will be LOCAL (your HOME/.pyenv and this directory)"
echo "[+]"
read -p "[+] Do you want to continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "[+] Exiting"
    exit 1
fi


# Configure the python environment with pyenv
# Check if pyenv is installed
if ! command -v pyenv &> /dev/null
then
    echo "[!!] pyenv could not be found"
    echo "[!!] Installing pyenv"
    curl https://pyenv.run | bash
    echo "[!!] Adding pyenv initialization to ~/.bashrc"
    echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
    echo 'eval "$(pyenv init -)"' >> ~/.bashrc
    echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
    source ~/.bashrc
else
    echo "[+] pyenv is already installed"
    source ~/.bashrc
fi

# Check if python 3.9.0 is installed
if ! pyenv versions | grep ${PYTHON_VERSION} &> /dev/null
then
    echo "[+] Installing Python ${PYTHON_VERSION}}"
    pyenv install ${PYTHON_VERSION}
fi

# Activate the python environment
echo "[+] Activating python ${PYTHON_VERSION}"
pyenv shell ${PYTHON_VERSION}


# Check if a folder called `.venv` exists in the current directory
if [ ! -d "${VENV_NAME}" ]
then
    echo "[+] Creating virtual environment"
    python -m venv ${VENV_NAME}
fi

# Activate virtual environment
echo "[+] Activating virtual environment"
source ${VENV_NAME}/bin/activate


# if [ ! -d "haddock3" ]
# then
#     echo "[+] Cloning HADDOCK3"
#     git clone --recursive https://github.com/haddocking/haddock3.git  >/dev/null 2>&1
# fi

# echo "[+] Installing/Updating HADDOCK3"
# cd haddock3
# cd src/fcc/src
# chmod u+x Makefile
# make  >/dev/null 2>&1
# cd -
# pip install -r requirements.txt  >/dev/null 2>&1
# # send stdout and err to null

# python setup.py develop   >/dev/null 2>&1

# echo "[+] Get the CNS binary"
# mkdir -p bin/
# curl https://surfdrive.surf.nl/files/index.php/s/f2Iy0Zg1xObSA69/download -o bin/cns  >/dev/null 2>&1
# chmod +x bin/cns
# cd ..


if [ ! -d "haddock3" ]
then
  echo "[+] Cloning HADDOCK3"
  git clone https://github.com/haddocking/haddock3.git >/dev/null 2>&1
fi

# Install haddock3
echo "[+] Installing/Updating HADDOCK3"
cd haddock3
git pull >/dev/null 2>&1
pip install .
cd ..


# Check if `haddock3` is installed
if ! command -v haddock3 &> /dev/null
then
    echo "[!!] HADDOCK3 could not be found"
    echo "[!!] Please check the installation"
    exit 1
fi

# Download the latest release of the `haddock-runner`
bash download-haddock-runner.sh

# Modify path in run_haddock.sh file
sed -i "s/_ABSPATH_PWD_/$PWD/g" run-haddock3.sh

echo "[+] Done"
