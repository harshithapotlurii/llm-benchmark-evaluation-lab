import argparse
import json
from pathlib import Path

from llm_eval.core import CompatibleProvider, FixtureProvider, evaluate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=("fixture", "compatible"), required=True)
    parser.add_argument("--output", type=Path, default=Path("results.json"))
    args = parser.parse_args()
    provider = FixtureProvider() if args.provider == "fixture" else CompatibleProvider()
    report = evaluate(provider)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
