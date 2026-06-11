import io
import json
import shutil
import sys
import zipfile
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
STATUS_JSON = ROOT / "paper" / "template_status.json"
URL = "https://github.com/ICLR/Master-Template/raw/master/iclr2026.zip"


def main():
    PAPER.mkdir(exist_ok=True)
    status = {"url": URL, "fetched": False, "files": [], "error": ""}
    try:
        response = requests.get(URL, timeout=60)
        response.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
            zf.extractall(PAPER / "_iclr2026_template")
        template_root = PAPER / "_iclr2026_template"
        for path in template_root.rglob("*"):
            if path.is_file() and path.suffix.lower() in [".sty", ".bst", ".tex", ".bib"]:
                dest = PAPER / path.name
                shutil.copyfile(path, dest)
                status["files"].append(path.name)
        status["fetched"] = True
    except Exception as exc:
        status["error"] = repr(exc)
    STATUS_JSON.write_text(json.dumps(status, indent=2), encoding="utf-8")
    print(json.dumps(status, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
