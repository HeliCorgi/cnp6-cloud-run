#!/usr/bin/env python3
"""Verify a graph JSON and a 5-coloring certificate.

Usage:
  python scripts/verify_checkpoint.py current/macro_cegis_30.json \
      current/macro_cegis_30_5.colors \
      --checkpoint current/macro_cegis_30_checkpoint.json
  python scripts/verify_checkpoint.py ... --geometry
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
import math
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('graph', type=Path)
    ap.add_argument('colors', type=Path)
    ap.add_argument('--checkpoint', type=Path)
    ap.add_argument('--geometry', action='store_true', help='check every registered edge length')
    ap.add_argument('--tol', type=float, default=3.0e-7)
    args = ap.parse_args()

    print(f'loading {args.graph} ...', flush=True)
    G = json.loads(args.graph.read_text())
    coords = G['coords']
    edges = G['edges']
    colors = [int(x) for x in args.colors.read_text().split()]

    if len(colors) != len(coords):
        raise SystemExit(f'FAIL color count {len(colors)} != vertices {len(coords)}')
    if any(c < 0 or c >= 5 for c in colors):
        raise SystemExit('FAIL a color is outside 0..4')

    bad = []
    for i, (u, v) in enumerate(edges):
        if colors[u] == colors[v]:
            bad.append((i, u, v, colors[u]))
            if len(bad) >= 20:
                break
    if bad:
        raise SystemExit(f'FAIL monochromatic edges: {bad}')

    graph_hash = sha256_file(args.graph)
    colors_hash = sha256_file(args.colors)
    counts = dict(sorted(collections.Counter(colors).items()))

    if args.checkpoint:
        C = json.loads(args.checkpoint.read_text())
        latest = C.get('latest', C)
        expected_g = latest.get('graph_sha256')
        expected_c = latest.get('colors_sha256')
        if expected_g and expected_g != graph_hash:
            raise SystemExit(f'FAIL graph hash {graph_hash} != {expected_g}')
        if expected_c and expected_c != colors_hash:
            raise SystemExit(f'FAIL colors hash {colors_hash} != {expected_c}')

    max_err = None
    over = None
    if args.geometry:
        max_err = 0.0
        over = 0
        for k, (u, v) in enumerate(edges, 1):
            x1, y1 = coords[u]
            x2, y2 = coords[v]
            err = abs(math.hypot(x1 - x2, y1 - y2) - 1.0)
            max_err = max(max_err, err)
            over += err > args.tol
            if k % 500000 == 0:
                print(f'geometry {k}/{len(edges)} max_err={max_err:.3e}', flush=True)
        if over:
            raise SystemExit(f'FAIL {over} registered edges exceed tolerance {args.tol}')

    print(json.dumps({
        'status': 'PASS',
        'vertices': len(coords),
        'edges': len(edges),
        'color_counts': counts,
        'graph_sha256': graph_hash,
        'colors_sha256': colors_hash,
        'max_registered_edge_error': max_err,
        'edges_over_tolerance': over,
    }, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
