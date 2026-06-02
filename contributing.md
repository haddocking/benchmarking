# Contributing to the HADDOCK Benchmarking Suite

Thank you for your interest in contributing. This benchmarking suite is intended to be a living resource that grows as new docking protocols, molecular systems, and datasets become available. Contributions of any kind are welcome — new scenarios, new benchmark datasets, improvements to the analysis pipeline, bug fixes, or documentation updates.

This document describes how to contribute effectively and what standards to follow.

## Getting Started

Before contributing, make sure you can run the suite locally. Follow the setup instructions in `Setup/README.MD` to install HADDOCK3, the virtual environment, and `haddock-runner`. Running an existing scenario end-to-end on a small test case is a good way to verify your environment and understand how the pieces fit together.

Fork the repository on GitHub and create a branch from `main` for your changes. Use a descriptive branch name that reflects what you are working on, for example:

```
feature/protein-rna-scenarios
fix/glycan-input-paths
docs/protein-peptide-readme
```

## What You Can Contribute

### New Benchmark Scenarios

The most common and valuable contribution is a new docking scenario — a YAML configuration file that tests a specific protocol, restraint strategy, or clustering approach. A good scenario contribution should:

- Be placed in the appropriate `Docking_benchmarks/<SystemType>/scenarios/` or `Docking_benchmarks/<SystemType>/Scenarios/` directory
- Follow the YAML structure of existing scenarios (see any existing `.yaml` file as a template)
- Use `_ABSPATH_PWD_` as a placeholder for all absolute paths — never hardcode paths to your local machine
- Include a descriptive `name:` field under the scenario block that reflects what the scenario tests
- Use the standardised SLURM settings: `partition: short`, `ncores: 40`, `max_concurrent: 10` (adjust only if there is a specific scientific reason)
- Be accompanied by an update to the README in the same subdirectory, explaining what the new scenario tests and why

### New Benchmark Systems

If you want to add an entirely new molecular system (e.g. protein-RNA, antibody-antigen, protein-carbohydrate with a new dataset), create a new subdirectory under `Docking_benchmarks/` following the naming convention `System_Type/`. The directory should contain:

- A `scenarios/` subdirectory with at least one YAML scenario file
- A `README.md` documenting the biological context, the dataset, and each scenario in detail (see existing READMEs for the expected level of detail)
- An input list file (or instructions on where to obtain one) formatted consistently with existing input lists

### Analysis Improvements

The analysis pipeline lives in `Analysis/`. Improvements to `AnalyseBenchmarkResults.py` — such as support for new metrics, additional plot types, or better output formatting — are welcome. If you change the output format, update `Analysis/README.md` accordingly.

### Bug Fixes and Path Issues

If a scenario YAML contains a broken path, incorrect parameter, or reproduces an error, open a GitHub issue first describing the problem and the expected behaviour, then submit a pull request with the fix.

### Documentation

If something is unclear, missing, or out of date in any README, feel free to improve it. Good documentation is as important as the scenarios themselves.

## Scenario YAML Style Guide

To keep all scenario files consistent and readable, follow these conventions:

- Use 2-space indentation throughout
- Do not hardcode absolute paths — always use `_ABSPATH_PWD_` as the base
- Do not include `haddock_dir:` or `executable:` fields — these are handled by the setup script
- Do not include a `parameters: / general: / clean: true` block — this is no longer used
- Keep one blank line between top-level YAML sections (`general:`, `scenarios:`)
- Do not add a blank line between `- name:` and `workflow:`
- Name your scenario with a short, descriptive slug that reflects the key distinguishing feature (e.g. `clustfcc`, `ab_initio`, `bound-unbound`)

Example of a well-formatted scenario header:

```yaml
general:
  input_list: _ABSPATH_PWD_/my-dataset/input.txt
  work_dir: _ABSPATH_PWD_/results/my_scenario

  execution: slurm
  partition: short
  ncores: 40
  max_concurrent: 10

  mol_suffixes:
    - _r_u
    - _l_u

scenarios:
  - name: my_scenario
    workflow:
      topoaa:
        autohis: true
      ...
```

## Pull Request Process

1. Make sure your changes work — if you added a scenario, test it on at least one target
2. Update the relevant README to document your addition
3. Run `git status` to confirm you are not accidentally committing swap files, compiled outputs, or local result directories
4. Open a pull request against `main` with a clear title and description of what was changed and why
5. Reference any related GitHub issues in the PR description

## Commit Message Style

Write commit messages in the imperative mood and keep the first line under 72 characters. Add a short body if the change needs more context.

```
add protein-RNA ab initio scenario

Uses random AIRs with RNA-specific dielectric settings.
Based on the same protocol as the protein-DNA bound-unbound scenario.
```

## What Not to Include

- Result files, PDB files, or large binary data — these belong in a separate data repository or should be downloaded at runtime
- Hardcoded paths to specific cluster home directories
- Personal credentials, API keys, or cluster-specific configuration
- Vim swap files (`.swp`), compiled Python files (`.pyc`), or editor artefacts

## License

By contributing to this repository, you agree that your contributions will be licensed under the Apache License 2.0, the same license that covers this project.
