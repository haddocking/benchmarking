# Contributing to the HADDOCK Benchmarking Suite

Thank you for your interest in contributing. This benchmarking suite is intended to be a scientific resource that grows as new docking protocols, molecular systems, and datasets become available. Contributions of any kind are welcome — new scenarios, new benchmark datasets, improvements to the analysis pipeline, bug fixes, or documentation updates.

This document describes how to contribute effectively and what standards to follow.

## What You Can Contribute

### New Benchmark Scenarios

The most common and valuable contribution is a new docking scenario — a YAML configuration file that tests a specific protocol, restraint strategy, or clustering approach. A good scenario contribution should:

- Be placed directly in the appropriate `Docking_benchmarks/<SystemType>/` directory (no `Scenarios/` subfolder, no `scenario_` filename prefix)
- Follow the YAML structure of existing scenarios (see any existing `.yaml` file as a template)


### New Benchmark Systems

If you want to add an entirely new molecular system (e.g. protein-RNA, antibody-antigen, protein-carbohydrate with a new dataset), create a new subdirectory under `Docking_benchmarks/` following the naming convention `System_Type/`. The directory should contain:

- At least one YAML scenario file, placed directly in the system directory
- A `README.md` documenting the biological context, the dataset, and each scenario in detail (see existing READMEs for the expected level of detail)
- An input list file (or instructions on where to obtain one) formatted consistently with existing input lists

### Analysis Improvements

The analysis pipeline lives in `Analysis/`. Improvements to `AnalyseBenchmarkResults.py` — such as support for new metrics, additional plot types, or better output formatting — are welcome. If you change the output format, update `Analysis/README.md` accordingly.

### Bug Fixes and Path Issues

If a scenario YAML contains a broken path, incorrect parameter, or reproduces an error, open a GitHub issue first describing the problem and the expected behaviour, then submit a pull request with the fix.

### Documentation

If something is unclear, missing, or out of date in any README, feel free to improve it. Good documentation is as important as the scenarios themselves.


## What Not to Include

- Result files, PDB files, or large binary data — these belong in a separate data repository or should be downloaded at runtime

## License

By contributing to this repository, you agree that your contributions will be licensed under the Apache License 2.0, the same license that covers this project.
