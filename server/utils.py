import os, json
from typing import Any, Dict

def ensure_dir(path:str) -> None:
    if not os.path.isdir(path):
        os.mkdir(path)

def ensure_file(path:str) -> None:
    ensure_parent(path)
    if not os.path.isfile(path):
        open(path, "w").close()

def ensure_parent(path:str) -> None:
    ensure_dir(os.path.dirname(path))

def open_json(path:str) -> Dict[str, Any]:
    with open(path) as f:
        return json.load(f)