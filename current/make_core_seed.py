import json,sys
full_old, colors_old, core_new, out=sys.argv[1:]
oldn=len(json.load(open(full_old))['coords'])
oldcol=list(map(int,open(colors_old).read().split()))
assert len(oldcol)==oldn
C=json.load(open(core_new)); n=len(C['coords']); orig=C['orig_vertices']
adj=[[] for _ in range(n)]
for u,v in C['edges']: adj[u].append(v);adj[v].append(u)
col=[-1]*n
for i,ov in enumerate(orig):
    if ov<oldn: col[i]=oldcol[ov]
# DSATUR-ish fill uncolored minimizing current conflicts, saturation/degree order dynamic
un=set(i for i,c in enumerate(col) if c<0)
while un:
    v=max(un,key=lambda x:(len({col[w] for w in adj[x] if col[w]>=0}),len(adj[x])))
    counts=[sum(col[w]==c for w in adj[v]) for c in range(5)]
    col[v]=min(range(5),key=lambda c:(counts[c],c))
    un.remove(v)
conf=sum(col[u]==col[v] for u,v in C['edges'])
open(out,'w').write('\n'.join(map(str,col))+'\n')
print('n',n,'newcore',sum(ov>=oldn for ov in orig),'seedconf',conf)
