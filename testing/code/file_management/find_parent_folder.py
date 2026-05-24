from pathlib import Path

def find_project_root(start: Path, folder_name="F1_Fantasy_v2") -> Path:
    for parent in [start] + list(start.parents):
        if parent.name == folder_name:
            return parent
    raise RuntimeError("Root not found")

current_file = Path(__file__).resolve()
PROJECT_ROOT = find_project_root(current_file)

data_raw = PROJECT_ROOT / "data" / "raw"

print(data_raw)