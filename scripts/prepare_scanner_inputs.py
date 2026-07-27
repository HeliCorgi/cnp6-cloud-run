#!/usr/bin/env python3
"""Create text inputs expected by core_robust_scan_shuf and multi_eval."""
from __future__ import annotations
import argparse, json
from pathlib import Path

def write_coords(path: Path, coords):
    with path.open('w') as f:
        f.write(f'{len(coords)}\n')
        for x,y in coords:
            f.write(f'{x:.17g} {y:.17g}\n')

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('graph', type=Path)
    ap.add_argument('core', type=Path)
    ap.add_argument('outdir', type=Path)
    ap.add_argument('--macro-size', type=int, default=16)
    args=ap.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    G=json.loads(args.graph.read_text())
    C=json.loads(args.core.read_text())
    write_coords(args.outdir/'graph.coords', G['coords'])
    write_coords(args.outdir/'macro16.coords', G['coords'][:args.macro_size])
    (args.outdir/'fixedmask.txt').write_text('\n'.join(map(str,C['orig_vertices']))+'\n')
    print('wrote', args.outdir/'graph.coords', args.outdir/'macro16.coords', args.outdir/'fixedmask.txt')
    return 0
if __name__=='__main__': raise SystemExit(main())
