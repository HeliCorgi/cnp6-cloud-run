#!/usr/bin/env python3
"""Select common-killer candidate lines with support diversity.

Input lines are produced by multi_eval.cpp:
 index kill total overlap fixed_overlap new_vertices mask support_csv
"""
from __future__ import annotations
import argparse
from pathlib import Path

def parse(path: Path):
    rows=[]
    for line in path.read_text().splitlines():
        if not line.strip(): continue
        a=line.split()
        idx,kill,total,ov,fov,new=map(int,a[:6])
        support=frozenset(int(x) for x in a[7].split(',') if x) if len(a)>7 else frozenset()
        rows.append({'idx':idx,'kill':kill,'total':total,'ov':ov,'fov':fov,'new':new,'support':support})
    return rows

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('eval_files', nargs='+', type=Path)
    ap.add_argument('--count', type=int, default=100)
    ap.add_argument('--output', required=True, type=Path)
    args=ap.parse_args()
    rows=[]
    for p in args.eval_files: rows.extend(parse(p))
    common=[r for r in rows if r['kill']==r['total'] and r['total']>0]
    # Prefer high fixed overlap, low number of new vertices, then broad new support.
    chosen=[]; used=set()
    while common and len(chosen)<args.count:
        best=max(common,key=lambda r:(
            len(r['support']-used), r['fov'], -r['new'], r['ov'], -r['idx']))
        chosen.append(best); used.update(best['support']); common.remove(best)
    args.output.write_text('\n'.join(str(r['idx']) for r in chosen)+'\n')
    print({'selected':len(chosen),'covered_support':len(used),'requested':args.count})
    if len(chosen)<args.count:
        print('WARNING: fewer common killers than requested')
    return 0
if __name__=='__main__': raise SystemExit(main())
