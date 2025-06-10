#!/usr/bin/env python3

import json
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

try:
    from jslot_to_transforms import extract_transforms
except ImportError:
    print("ERROR: Could not import extract_transforms from jslot_to_transforms.py")
    sys.exit(1)


def apply_transforms_to_nif(transforms_dict, nif_in_path, nif_out_path, clamp_value=None):
    from collections import defaultdict
    from pyffi.formats.nif import NifFormat

    def clamp(v: float, lim: float):
        return max(-lim, min(lim, v)) if lim is not None else v

    trans_map = {}
    scale_lists = defaultdict(list)

    for bone_name, xf in transforms_dict.items():
        if "Cam" in bone_name:
            continue
        tr = xf.get("translation")
        if not (isinstance(tr, (list, tuple)) and len(tr) == 3):
            continue
        tx = clamp(tr[0], clamp_value)
        ty = clamp(tr[1], clamp_value)
        tz = clamp(tr[2], clamp_value)
        trans_map[bone_name] = (tx, ty, tz)
        sc = xf.get("scale")
        if isinstance(sc, (int, float)):
            scale_lists[bone_name].append(float(sc))

    if not trans_map:
        raise RuntimeError("No valid entries to apply.")

    data = NifFormat.Data()
    try:
        with open(nif_in_path, "rb") as fp:
            data.read(fp)
    except Exception as e:
        raise RuntimeError(f"ERROR: cannot open/parse NIF file {nif_in_path}: {e}")

    def assign_parents(node, parent=None):
        node._parent = parent
        for c in node.children:
            if isinstance(c, NifFormat.NiNode):
                assign_parents(c, node)

    def walk_nodes(root):
        stack = [root]
        while stack:
            n = stack.pop()
            if isinstance(n, NifFormat.NiNode):
                yield n
                stack.extend(n.children)

    lookup = {}
    for rootnode in data.roots:
        assign_parents(rootnode, None)
        for node in walk_nodes(rootnode):
            try:
                nm = node.name.decode("utf-8")
            except Exception:
                continue
            lookup[nm] = node

    for bone_name, (tx, ty, tz) in trans_map.items():
        node = lookup.get(bone_name)
        if node is None:
            continue
        node.translation.x = float(tx)
        node.translation.y = float(ty)
        node.translation.z = float(tz)

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
        with open(nif_out_path, "wb") as fp:
            data.write(fp)
    except Exception as e:
        raise RuntimeError(f"ERROR: could not save NIF file {nif_out_path}: {e}")


def main():
    root = tk.Tk()
    root.withdraw()

    messagebox.showinfo(
        "NIF Skeleton Baker",
        "Select a RaceMenu .jslot file and an input skeleton .nif.\n"
        "The baked .nif will be saved alongside the original with 'BAKED' appended."
    )

    jslot_path = filedialog.askopenfilename(
        title="NIF Skeleton Baker: Select RaceMenu .jslot",
        filetypes=[("RaceMenu JSlot", "*.jslot"), ("All files", "*.*")]
    )
    if not jslot_path:
        sys.exit("No .jslot selected. Exiting.")

    nif_in_path = filedialog.askopenfilename(
        title="NIF Skeleton Baker: Select input skeleton .nif",
        filetypes=[("NIF File", "*.nif"), ("All files", "*.*")]
    )
    if not nif_in_path:
        sys.exit("No input .nif selected. Exiting.")

    inp = Path(nif_in_path)
    output_name = inp.stem + "BAKED" + inp.suffix
    nif_out_path = str(inp.parent / output_name)

    try:
        with open(jslot_path, "r", encoding="utf-8") as fp:
            jslot_data = json.load(fp)
    except Exception as e:
        messagebox.showerror("NIF Skeleton Baker: Error", f"Failed to read .jslot file:\n{e}")
        sys.exit(1)

    try:
        transforms = extract_transforms(jslot_data)
    except Exception as e:
        messagebox.showerror("NIF Skeleton Baker: Error", f"Failed to extract transforms from .jslot:\n{e}")
        sys.exit(1)

    clamp_val = None

    try:
        apply_transforms_to_nif(transforms, nif_in_path, nif_out_path, clamp_val)
    except Exception as e:
        messagebox.showerror("NIF Skeleton Baker: Error", f"Failed to bake skeleton .nif:\n{e}")
        sys.exit(1)

    messagebox.showinfo(
        "NIF Skeleton Baker",
        f"Successfully wrote baked .nif to:\n{nif_out_path}"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
