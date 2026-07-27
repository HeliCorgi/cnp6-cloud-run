import json,collections,time,sys
inp=sys.argv[1];outp=sys.argv[2]
G=json.load(open(inp)); n=len(G['coords']); adj=[set() for _ in range(n)]
for u,v in G['edges']:adj[u].add(v);adj[v].add(u)
alive=[True]*n; deg=[len(x) for x in adj]; peel=[]; dom=[]; ops=[]
q=collections.deque(i for i,d in enumerate(deg) if d<5)
def remove_low(v):
 alive[v]=False;peel.append(v);ops.append(['low',v])
 for w in list(adj[v]):
  if alive[w]:
   deg[w]-=1
   if deg[w]<5:q.append(w)
def drain():
 while q:
  v=q.popleft()
  if alive[v] and deg[v]<5:remove_low(v)
drain();roundno=0;t0=time.time()
while True:
 roundno+=1; removed=0
 verts=[v for v in range(n) if alive[v]]
 verts.sort(key=lambda v:deg[v])
 for ii,v in enumerate(verts):
  if not alive[v] or deg[v]<5:continue
  nv=[w for w in adj[v] if alive[w]]
  if not nv:continue
  w=min(nv,key=lambda x:deg[x])
  # dominator u must be neighbor of each member of N(v), start with N(w)
  cand=[u for u in adj[w] if alive[u] and u!=v and u not in adj[v] and deg[u]>=deg[v]]
  Sv=set(nv)
  for u in cand:
   if Sv.issubset(adj[u]):
    alive[v]=False;dom.append((v,u));ops.append(['dom',v,u]);removed+=1
    for x in nv:
     deg[x]-=1
     if deg[x]<5:q.append(x)
    break
  if ii%500==0: pass
 drain()
 print('round',roundno,'alive',sum(alive),'dom_total',len(dom),'peel',len(peel),'removed',removed,'time',round(time.time()-t0,2),flush=True)
 if removed==0:break
core=[i for i,a in enumerate(alive) if a];idx={v:i for i,v in enumerate(core)};E=[]
for u,v in G['edges']:
 if alive[u] and alive[v]:E.append([idx[u],idx[v]])
out={'coords':[G['coords'][v] for v in core], 'edges':E,'orig_vertices':core,'peel_order':peel,'domination':dom,'reduction_ops':ops,'source':inp}
json.dump(out,open(outp,'w'))
print('final',len(core),len(E))
