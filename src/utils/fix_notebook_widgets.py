import json
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

for filepath in PROJECT_ROOT.glob("**/*.ipynb"):
    if ".ipynb_checkpoints" in filepath.parts:
        continue

    with open(filepath, "r", encoding="utf-8") as f:
        nb = json.load(f)

    widgets_meta = nb.get("metadata", {}).get("widgets")
    if widgets_meta:
        del nb["metadata"]["widgets"]
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(nb, f, indent=1)
        print(f"Cleaned: {filepath}")