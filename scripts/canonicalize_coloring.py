#!/usr/bin/env python3
"""Canonicalize a coloring under global color permutation and print SHA-256."""
from __future__ import annotations
import argparse, hashlib
from pathlib import Path

def canonical(colors: list[int]) -> list[int]:
    mp: dict[int, int] = {}
    nxt = 0
    out = []
    for c in colors:
        if c not in mp:
            mp[c] = nxt
            nxt += 1
        out.append(mp[c])
    return out

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('input', type=Path)
    ap.add_argument('--output', type=Path)
    args=ap.parse_args()
    colors=[int(x) for x in args.input.read_text().split()]
    can=canonical(colors)
    text='\n'.join(map(str,can))+'\n'
    if args.output:
        args.output.write_text(text)
    print(hashlib.sha256(text.encode()).hexdigest())
    return 0
if __name__=='__main__': raise SystemExit(main())
