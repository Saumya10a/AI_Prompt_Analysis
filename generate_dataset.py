#!/usr/bin/env python
import sys
import argparse
import shutil
from pathlib import Path

backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.dataset_generator import DatasetGenerator
from app.core.config import settings


def main():
    parser = argparse.ArgumentParser(description="Generate the synthetic BDA prompt dataset.")
    parser.add_argument("--records", type=int, default=100_000, help="Number of prompt records (default: 100000)")
    args = parser.parse_args()

    project_root = Path(__file__).parent
    configured_path = Path(settings.dataset_path)
    if not configured_path.is_absolute():
        configured_path = project_root / configured_path
    print(f"Generating {args.records:,} records at: {configured_path}")
    generator = DatasetGenerator(str(configured_path), num_records=args.records)
    count = generator.generate_and_save()
    print(f"Generated {count} records")
    backend_path = project_root / "backend" / "data" / "sample_dataset.jsonl"
    if backend_path.resolve() != configured_path.resolve():
        backend_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(configured_path, backend_path)
        print(f"Synchronized backend dataset: {backend_path}")
    print("Dataset generation complete")


if __name__ == "__main__":
    main()
