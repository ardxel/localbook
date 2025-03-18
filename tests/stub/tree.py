import os
from typing import Any


def stub_tree(base_dir: str, structure: dict[str, Any]):
    for name, content in structure.items():
        current_path = os.path.join(base_dir, name)

        if isinstance(content, dict):
            os.makedirs(current_path, exist_ok=True)
            stub_tree(current_path, content)
        else:
            os.makedirs(os.path.dirname(current_path), exist_ok=True)
            with open(current_path, "w") as f:
                f.write(name)
