#!/usr/bin/env python3

import json
import sys
import argparse
from collections import defaultdict
from pyffi.formats.nif import NifFormat

def clamp(v: float, lim: float):
    return max(-lim, min(lim, v)) if lim is not None else v

def assign_parents(node, parent=None):
    node._parent = parent
    for c in node.children:
        if isinstance(c, NifFormat.NiNode):
            assign_parents(c, node)

def walk(root):
    stack = [root]
    while stack:
        n = stack.pop()
        if isinstance(n, NifFormat.NiNode):
            yield n
            stack.extend(n.children)

ap = argparse.ArgumentParser()
ap.add_argument("json", help="path to transforms_output.json")
ap.add_argument("nif_in", help="input NIF")
ap.add_argument("nif_out", help="output NIF")
ap.add_argument("--clamp", type=float, default=None)
args = ap.parse_args()

try:
    raw = json.load(open(args.json, "r", encoding="utf-8"))
except Exception as e:
    print(f"ERROR: cannot open/parse JSON file {args.json}: {e}")
    sys.exit(1)

trans_map = {}
scale_lists = defaultdict(list)

for bone_name, xf in raw.items():
    if "Cam" in bone_name:
        continue
    tr = xf.get("translation")
    if not (isinstance(tr, list) and len(tr) == 3):
        continue
    tx, ty, tz = tr
    tx = clamp(tx, args.clamp)
    ty = clamp(ty, args.clamp)
    tz = clamp(tz, args.clamp)
    trans_map[bone_name] = (tx, ty, tz)
    sc = xf.get("scale")
    if isinstance(sc, (int, float)):
        scale_lists[bone_name].append(float(sc))

if not trans_map:
    sys.exit(0)

data = NifFormat.Data()
try:
    with open(args.nif_in, "rb") as fp:
        data.read(fp)
except Exception as e:
    print(f"ERROR: cannot open/parse NIF file {args.nif_in}: {e}")
    sys.exit(1)

lookup = {}
for root in data.roots:
    assign_parents(root, None)
    for node in walk(root):
        try:
            nm = node.name.decode("utf-8")
        except Exception:
            continue
        lookup[nm] = node

for bone_name, (tx, ty, tz) in trans_map.items():
    node = lookup.get(bone_name)
    if node is None:
        continue
    node.translation.x = tx
    node.translation.y = ty
    node.translation.z = tz
    sliders = scale_lists.get(bone_name, [])
    if not sliders:
        continue
    prod = 1.0
    for s in sliders:
        prod *= s
    if bone_name in ("NPC L Hand [LHnd]", "NPC R Hand [RHnd]"):
        orig = float(node.scale)
        node.scale = orig * prod
    else:
        node.scale = prod

try:
    with open(args.nif_out, "wb") as fp:
        data.write(fp)
except Exception as e:
    print(f"ERROR: could not save NIF file {args.nif_out}: {e}")
    sys.exit(1)
