import json,sys,math
Gp,Kp,Lp,Out=sys.argv[1:5];G=json.load(open(Gp));rows=open(Kp).read().splitlines();lines=[int(x) for x in open(Lp) if x.strip()];coords=[tuple(p) for p in G['coords']];key=lambda p:(round(p[0]*1e8),round(p[1]*1e8));idx={key(p):i for i,p in enumerate(coords)};E={tuple(sorted(e)) for e in G['edges']};M=[tuple(p) for p in G['coords'][:16]];MU=[(i,j) for i in range(16) for j in range(i+1,16) if abs(math.dist(M[i],M[j])-1)<3e-7]
cell=1.05;grid={}
def gkey(p):return (math.floor(p[0]/cell),math.floor(p[1]/cell))
for i,p in enumerate(coords):grid.setdefault(gkey(p),[]).append(i)
placements=[];totalnew=0
for z,ln in enumerate(lines):
 a=rows[ln].split();ov,fov=map(int,a[1:3]);vals=list(map(float,a[3:]));P=[(vals[2*i],vals[2*i+1]) for i in range(16)];ids=[];new=[]
 for p in P:
  v=idx.get(key(p))
  if v is None or math.dist(coords[v],p)>=4e-7:
   v=len(coords);coords.append(p);idx[key(p)]=v;grid.setdefault(gkey(p),[]).append(v);new.append(v);totalnew+=1
  ids.append(v)
 for v in new:
  p=coords[v];bx,by=gkey(p)
  for dx in (-1,0,1):
   for dy in (-1,0,1):
    for u in grid.get((bx+dx,by+dy),[]):
     if u<v and abs(math.dist(coords[u],p)-1)<3e-7:E.add((u,v))
 for i,j in MU:E.add(tuple(sorted((ids[i],ids[j]))))
 placements.append({'line':ln,'reported_overlap':ov,'fixed_overlap':fov,'actual_new':len(new),'ids':ids})
 if (z+1)%100==0:print('added placements',z+1,'vertices',len(coords),'edges',len(E),flush=True)
out={'coords':[list(p) for p in coords],'edges':[list(e) for e in sorted(E)],'parent':Gp,'step':G.get('step',0)+1,'killer_type':'core_robust_batch1000','batch_lines':lines,'placements':placements};json.dump(out,open(Out,'w'));print('FINAL old',len(G['coords']),len(G['edges']),'new',len(coords),len(E),'added',totalnew)
