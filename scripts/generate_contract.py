"""Run from the repository root: python -m scripts.generate_contract."""
import json
from pathlib import Path

from backend.app.models import ArtifactGraph


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    output = root / "shared" / "artifact_schema.json"
    output.parent.mkdir(exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as file:
        file.write(json.dumps(ArtifactGraph.model_json_schema(), indent=2) + "\n")
    print(output)
