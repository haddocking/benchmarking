# Adding a scenario

How to add a new docking scenario to an existing benchmark system, using the `gen-decoys` scenario added to `docking_benchmarks/protein_dna/` as a worked example.

## Where it goes

Scenario YAMLs live directly under `docking_benchmarks/<system>/`:

```text
docking_benchmarks/protein_dna/gen-decoys.yaml
```

## Anatomy of a scenario file

See the [haddock-runner docs](https://www.bonvinlab.org/haddock-runner/home.html) for a full description of the scenario file, below you see a simple example:

```yaml
general:
  input_list: prot-dna-input.txt        # bare filename, not a path
  work_dir: benchmark_output/gen-decoys # relative, colocated with the YAML

  execution: slurm
  partition: short
  gen_archive: true
  ncores: 40
  max_concurrent: 10

  mol_suffixes:
    - _p1_u
    - _p2_u
    - _d_u

scenarios:
  - name: decoys
    workflow:
      topoaa:
      rigidbody:
        sampling: 1000
      caprieval:
        reference_fname: _target.pdb
```


## Documenting it

Every scenario needs an entry in its system's `README.md`, under `## Scenarios`, and you explain what this configuration file was setup for:

```markdown
### gen-decoys

Both protein and DNA are unbound, and no interface restraints are used...
```

Explain what makes this scenario different from its siblings (restraint strategy, sampling depth, what stages are skipped, what question it answers).

## Verify before committing

```bash
python3 -c "import yaml; yaml.safe_load(open('docking_benchmarks/<system>/<scenario>.yaml'))"
./run.sh docking_benchmarks/<system>/<scenario>.yaml
```

A real run needs the dataset staged (`bash docking_benchmarks/<system>/setup.sh`, or it's already staged if you ran the root `setup.sh`).

## What `gen-decoys` illustrates

The other `protein_dna` scenarios (`bound-bound`, `bound-unbound`, `unbound-unbound`) each run a full pipeline: `rigidbody` → `seletop` → `flexref` → `mdref` → `clustfcc` → `seletopclusts`, with a `caprieval` after every stage, scoring against known restraints (`ambig_fname`). `gen-decoys` is deliberately smaller and serves a different purpose it just generates a large pool of raw decoys rather than benchmarking a refinement protocol:

- `rigidbody` uses `ranair: true` instead of a restraint file — no assumed interface, samples the whole surface.
- `sampling: 1000`, no `seletop`/refinement/clustering after it.
- A single `caprieval` scores the raw decoy set as-is.

Not every scenario needs to be a full benchmark protocol — match the workflow's shape to what the scenario is actually for.
