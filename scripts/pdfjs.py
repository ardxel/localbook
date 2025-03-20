# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "requests",
# ]
# ///

import os
import shutil
import zipfile

import requests
from _config import git_root

ROOT = git_root()
with open(os.path.join(ROOT, ".pdfjs-version"), "r") as version_file:
    version = version_file.read().rstrip()

zip_file = f"pdfjs-{version}-dist.zip"
url = f"https://github.com/mozilla/pdf.js/releases/download/v{version}/{zip_file}"
save_to = os.path.join(ROOT, "static/packages/pdfjs")


def main() -> None:
    if os.path.exists(save_to):
        shutil.rmtree(save_to)

    try:
        response = requests.get(url, stream=True)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    with open(zip_file, mode="wb") as file:
        for chunk in response.iter_content(chunk_size=10 * 1024):
            file.write(chunk)

    if not os.path.exists(zip_file):
        raise FileNotFoundError(f"Archive not found: {zip_file}")
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(save_to)
    os.remove(zip_file)

    print(f"pdf.js version: {version}")
    print(f"loaded successfully in {save_to}")


if __name__ == "__main__":
    main()
