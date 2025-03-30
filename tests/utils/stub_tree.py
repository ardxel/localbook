import os
from typing import Any


def create_stub_tree(base_dir: str, structure: dict[str, Any]):
    for name, content in structure.items():
        current_path = os.path.join(base_dir, name)

        if isinstance(content, dict):  # Если это папка
            os.makedirs(current_path, exist_ok=True)
            create_stub_tree(current_path, content)
        elif content is None:
            os.makedirs(os.path.dirname(current_path), exist_ok=True)
            with open(current_path, "w") as f:
                f.write(name)
        elif isinstance(content, str):
            os.makedirs(os.path.dirname(current_path), exist_ok=True)

            if not os.path.exists(content):
                print("File is not exist")
                continue

            with open(content, "rb") as original:
                with open(current_path, "wb") as fake:
                    fake.write(original.read())
