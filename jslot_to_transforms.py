#!/usr/bin/env python

import json
import sys
from pathlib import Path

def extract_transforms(jslot):
    result = {}
    for entry in jslot.get("transforms", []):
        node_name = entry["node"]
        translation = [0, 0, 0]
        scale = None
        for keyset in entry["keys"]:
            for val in keyset["values"]:
                k = val["key"]
                idx = val["index"]
                if k == 31 and idx in (0, 1, 2):
                    translation[idx] = val["data"]
                elif k == 30 and idx == 0:
                    scale = val["data"]
        result[node_name] = {"translation": translation, "scale": scale}
    return result

def main():
    if len(sys.argv) != 3:
        sys.exit("Usage: python jslot_to_transforms.py input.jslot output.json")
    in_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    with in_path.open(encoding="utf-8") as fp:
        jslot_data = json.load(fp)
    transforms = extract_transforms(jslot_data)
    with out_path.open("w", encoding="utf-8") as fp:
        json.dump(transforms, fp, indent=2)
    print(f"✓ Wrote {len(transforms)} nodes → {out_path}")

if __name__ == "__main__":
    main()
