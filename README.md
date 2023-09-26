# HADDOCK Benchmarking Suite

This repository contains the benchmarking suite for the HADDOCK software suite.

## Setup and Installation

**VERY IMPORTANT: Here we will NOT use anaconda, nor a global installation of Haddock or Python.**

Everything must be installed in the current directory, this is to avoid conflicts with other software and keep the system clean.

We will use `pyenv` to manage the python version and virtual environments.

The setup will be **LOCAL nothing will be changed in the cluster for other users**.

1. Install `pyenv`
2. Compile Python 3.9.18
3. Create a virtual environment with Python 3.9.18
4. Clone `haddock3` repository
5. Install `haddock3` in the virtual environment
6. Download a static pre-compilled CNS binary
7. Download the latest version of `haddock-runner`

```bash
bash setup-tintin.sh
```

## Usage

Simply run:

```
./haddock-runner <config-file>.yml
```

You don't need to activate the virtual environment or wory about python, the `haddock-runner` takes care of it.