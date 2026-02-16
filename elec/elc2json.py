#!/usr/bin/env python3
"""
elc2json.py

Usage:
    python elc2json.py <input.tsv> <output.json> [options]

Reads a TSV with columns:
    Labels  X   Y   Z
(or similar header names). Produces a JSON file with the structure requested:
{
  "name": "<input filename without ext>",
  "nodeColormap": "nih",
  "nodeMinColor": 1,
  "nodeMaxColor": 2,
  "nodeScale": 1,
  "legendLineThickness": 0,
  "nodes": [ { "name":..., "x":..., "y":..., "z":..., "colorValue":1, "sizeValue":1 }, ... ]
}

Filtering options (inclusive):
  --xmin, --xmax, --ymin, --ymax, --zmin, --zmax

If a bound isn't provided, that axis is unbounded on that side.
"""

import argparse
import csv
import json
import os
import sys

def parse_args():
    p = argparse.ArgumentParser(description="Convert electrode TSV (Label X Y Z) to JSON nodes with optional coordinate filtering.")
    p.add_argument("input_tsv", help="Input TSV file (tab-separated). First row may be a header.")
    p.add_argument("output_json", help="Output JSON filename.")
    p.add_argument("--xmin", type=float, help="Minimum X (inclusive).")
    p.add_argument("--xmax", type=float, help="Maximum X (inclusive).")
    p.add_argument("--ymin", type=float, help="Minimum Y (inclusive).")
    p.add_argument("--ymax", type=float, help="Maximum Y (inclusive).")
    p.add_argument("--zmin", type=float, help="Minimum Z (inclusive).")
    p.add_argument("--zmax", type=float, help="Maximum Z (inclusive).")
    p.add_argument("--skip-header", action="store_true", help="Force skipping the first line as header.")
    return p.parse_args()

def guess_columns(header):
    """Given a list of header names (lower-cased), find indices for label/x/y/z.
       Return tuple (label_idx, x_idx, y_idx, z_idx) or (None,...) if cannot find.
    """
    h = [c.strip().lower() for c in header]
    label_candidates = ["label", "labels", "name", "elec", "electrode", "channel"]
    x_candidates = ["x", "x(mm)", "xcoord", "x_coord", "x_mm"]
    y_candidates = ["y", "y(mm)", "ycoord", "y_coord", "y_mm"]
    z_candidates = ["z", "z(mm)", "zcoord", "z_coord", "z_mm"]
    def find_one(cands):
        for cand in cands:
            if cand in h:
                return h.index(cand)
        # try startswith / contains
        for i, col in enumerate(h):
            for cand in cands:
                if cand in col:
                    return i
        return None
    return find_one(label_candidates), find_one(x_candidates), find_one(y_candidates), find_one(z_candidates)

def in_bounds(x, xmin, xmax):
    if xmin is not None and x < xmin:
        return False
    if xmax is not None and x > xmax:
        return False
    return True

def main():
    args = parse_args()

    # Basic checks
    if not os.path.exists(args.input_tsv):
        print(f"ERROR: input file not found: {args.input_tsv}", file=sys.stderr)
        sys.exit(2)

    nodes = []
    with open(args.input_tsv, newline='') as fh:
        # We'll use csv reader with tab delimiter but be permissive if it's space-separated
        # Read first line to inspect header
        first = fh.readline()
        if not first:
            print("ERROR: input file is empty", file=sys.stderr)
            sys.exit(3)
        # Detect delimiter heuristically
        delimiter = '\t' if '\t' in first else None
        if delimiter is None:
            # fallback: try splitting on any whitespace using csv with delimiter ' '
            delimiter = '\t'  # we'll still try csv.Sniffer to be safe below

        # Rewind file and use sniffer
        fh.seek(0)
        sample = fh.read(2048)
        fh.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters="\t ,")
        except csv.Error:
            dialect = csv.get_dialect('excel')
            dialect.delimiter = '\t'
        reader = csv.reader(fh, dialect)
        # Peek first row
        rows = []
        try:
            first_row = next(reader)
        except StopIteration:
            first_row = []
        # Determine if first row is header by heuristic (contains non-numeric in X/Y/Z columns)
        header = [c.strip() for c in first_row] if first_row else []
        label_idx = x_idx = y_idx = z_idx = None

        if header and not args.skip_header:
            # Try to find columns
            label_idx, x_idx, y_idx, z_idx = guess_columns(header)
            # If we successfully found numeric columns, treat as header; else re-interpret as data row
            if None in (label_idx, x_idx, y_idx, z_idx):
                # Maybe there's no header; treat this row as data
                rows.append(first_row)
            # else header consumed; continue reading data rows
        else:
            # header skip or empty header: treat first_row as data
            rows.append(first_row)

        # Read remainder
        for r in reader:
            if r and any(cell.strip() for cell in r):
                rows.append(r)

    # If we didn't detect columns earlier (no header), try to infer by position:
    if None in (label_idx, x_idx, y_idx, z_idx):
        # common layout: label at 0, x 1, y 2, z 3
        if rows and len(rows[0]) >= 4:
            label_idx, x_idx, y_idx, z_idx = 0, 1, 2, 3
        else:
            print("ERROR: couldn't determine columns automatically. Provide a header or use --skip-header to force treating the first line as data.", file=sys.stderr)
            sys.exit(4)

    # Parse rows into nodes
    for r in rows:
        # guard against short rows
        if len(r) <= max(label_idx, x_idx, y_idx, z_idx):
            # skip or warn
            continue
        name = r[label_idx].strip()
        if name == "":
            continue
        # parse floats robustly (remove commas)
        try:
            x = float(r[x_idx].strip().replace(',', ''))
            y = float(r[y_idx].strip().replace(',', ''))
            z = float(r[z_idx].strip().replace(',', ''))
        except Exception:
            # If parsing failed, skip this row
            # (could optionally log a warning)
            continue

        if not (in_bounds(x, args.xmin, args.xmax) and
                in_bounds(y, args.ymin, args.ymax) and
                in_bounds(z, args.zmin, args.zmax)):
            continue

        nodes.append({
            "name": name,
            "x": x,
            "y": y,
            "z": z,
            "colorValue": 1,
            "sizeValue": 1
        })

    out = {
        "name": os.path.splitext(os.path.basename(args.input_tsv))[0],
        "nodeColormap": "nih",
        "nodeMinColor": 1,
        "nodeMaxColor": 2,
        "nodeScale": 1,
        "legendLineThickness": 0,
        "nodes": nodes
    }

    # Write pretty JSON
    with open(args.output_json, "w", newline='\n') as ofh:
        json.dump(out, ofh, indent=2, sort_keys=False)
        ofh.write("\n")

    print(f"Wrote {len(nodes)} nodes to {args.output_json}")

if __name__ == "__main__":
    main()
