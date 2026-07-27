import json,sys,collections,hashlib
fullp,corep,seedp,tabup,outp=sys.argv[1:6]
G=json.load(open(fullp));C=json.load(open(corep));seed=list(map(int,open(seedp).read().split()));colc=seed[:]
if tabup!='-':
 for l in open(tabup):
  i,c=map(int,l.split());colc[i]=c
assert len(colc)==len(C['coords'])
assert all(colc[u]!=colc[v] for u,v in C['edges'])
n=len(G['coords']);col=[-1]*n
for i,ov in enumerate(C['orig_vertices']):col[ov]=colc[i]
adj=[[] for _ in range(n)]
for u,v in G['edges']:adj[u].append(v);adj[v].append(u)
if C.get('reduction_ops'):
 for op in reversed(C['reduction_ops']):
  if op[0]=='dom':
   _,v,u=op; col[v]=col[u]
  else:
   _,v=op; used={col[w] for w in adj[v] if col[w]>=0}; av=[c for c in range(5) if c not in used]
   if not av: raise RuntimeError(('low-extend',v,used))
   col[v]=av[0]
else:
 for v in reversed(C['peel_order']):
  used={col[w] for w in adj[v] if col[w]>=0};av=[c for c in range(5) if c not in used]
  if not av:raise RuntimeError((v,used))
  col[v]=av[0]
 for v,u in reversed(C.get('domination',[])):
  if col[v]<0: col[v]=col[u]
assert all(c>=0 for c in col)
bad=[(u,v) for u,v in G['edges'] if col[u]==col[v]];assert not bad
open(outp,'w').write('\n'.join(map(str,col))+'\n')
cert={'graph':fullp,'vertices':n,'edges':len(G['edges']),'counts':dict(collections.Counter(col)),'bad_edges':0,'sha256_colors':hashlib.sha256(('\n'.join(map(str,col))+'\n').encode()).hexdigest(),'sha256_graph':hashlib.sha256(open(fullp,'rb').read()).hexdigest()}
json.dump(cert,open(outp.rsplit('.',1)[0]+'_certificate.json','w'),indent=2)
print(cert)
