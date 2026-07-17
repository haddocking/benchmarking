#!/usr/bin/env python3
"""Convert a haddock-runner `summary.json` file into two flat CSVs."""

import argparse
import csv
import json
from pathlib import Path


def build_rows(data: dict):
    """Flatten a summary.json dict into (scenario_rows, job_rows)."""
    scenario_rows = []
    for scenario in data.get("scenarios", []):
        scenario_rows.append(
            {
                "scenario_name": scenario["name"],
                "scenario_total": scenario["total"],
                "scenario_completed": scenario["completed"],
                "scenario_skipped": scenario["skipped"],
                "scenario_failed": scenario["failed"],
                "scenario_duration_secs": scenario["duration_secs"],
            }
        )

    job_rows = []
    for job in data.get("jobs", []):
        job_rows.append(
            {
                "job_name": job["name"],
                "scenario": job["scenario"],
                "target": job["target"],
                "status": job["status"],
                "duration_secs": job["duration_secs"],
            }
        )

    return scenario_rows, job_rows


def write_csv(path: Path, rows: list) -> None:
    """Write rows (list of dicts) to path as CSV, or an empty file if none."""
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    """Parse CLI args, convert the given summary.json, and write the two CSVs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary_json", type=Path, help="Path to a summary.json file")
    parser.add_argument(
        "suffix",
        help="Suffix appended to output filenames, e.g. 'sha' -> scenarios_sha.csv",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path.cwd(),
        help="Directory to write the CSVs into (default: cwd)",
    )
    args = parser.parse_args()

    data = json.loads(args.summary_json.read_text())
    scenario_rows, job_rows = build_rows(data)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    scenarios_path = args.output_dir / f"scenarios_{args.suffix}.csv"
    jobs_path = args.output_dir / f"jobs_{args.suffix}.csv"

    write_csv(scenarios_path, scenario_rows)
    write_csv(jobs_path, job_rows)

    print(
        f"Wrote {len(scenario_rows)} scenario rows to {scenarios_path}\n"
        f"Wrote {len(job_rows)} job rows to {jobs_path}"
    )


if __name__ == "__main__":
    main()
