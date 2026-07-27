import numpy as np, sys, os, json, time
sys.path.insert(0,'/mnt/data');import distforge_robust as R
from local6_utils import local_find, canon
NPZ='/mnt/data/distforge_pairs.npz';STATE='/mnt/data/local6_state.json';LOG='/mnt/data/local6_fast.jsonl';P=R.P;Q=R.Q;N=R.N
valid=np.array([v for v in range(N) if v not in (P,Q)],dtype=np.int32);L=len(valid)
z=np.load(NPZ);A=z['alphas'].copy();B=z['betas'].copy()
def rowD(a,b):
 p=((a[valid]==a[P])==(b[valid]==b[P])); q=((a[valid]==a[Q])==(b[valid]==b[Q]));return np.concatenate([~p,~q])
def allD(A,B):
 p=((A[:,valid]==A[:,[P]])==(B[:,valid]==B[:,[P]]));q=((A[:,valid]==A[:,[Q]])==(B[:,valid]==B[:,[Q]]));return np.concatenate([~p,~q],axis=1)
D=allD(A,B);seen={(canon(x),canon(y)) for x,y in zip(A,B)}
start=None
if os.path.exists(STATE):
 try:start=np.array(json.load(open(STATE))['sel'],int)
 except:pass
def atoms(sel):return [(P,int(valid[x])) for x in sel[:3]]+[(Q,int(valid[x-L])) for x in sel[3:]]
def save():
 t=NPZ+'.tmp.npz';np.savez(t,alphas=A,betas=B);os.replace(t,NPZ)
def emit(rec):
 with open(LOG,'a') as f:f.write(json.dumps(rec)+'\n')
iters=int(sys.argv[1]) if len(sys.argv)>1 else 500; added=0;tall=time.time()
for it in range(iters):
 t=time.time();sel,sc=local_find(D,start,restarts=10,steps=40)
 if sel is None:
  rec={'it':it,'pairs':len(A),'master':'NO_HEURISTIC','best_uncovered':sc,'sec':time.time()-t};print(json.dumps(rec),flush=True);emit(rec);break
 at=atoms(sel);st,a,b,sec,meta=R.oracle_atoms(at,8000000+len(A)+it,limit=20)
 rec={'it':it,'pairs_before':len(A),'sel':sel.tolist(),'atoms':at,'master_sec':time.time()-t-sec,'oracle':st,'oracle_sec':sec}
 if st=='SAT':
  k=(canon(a),canon(b));new=k not in seen
  if new:
   seen.add(k);A=np.vstack([A,np.asarray(a,np.uint8)]);B=np.vstack([B,np.asarray(b,np.uint8)]);D=np.vstack([D,rowD(np.asarray(a),np.asarray(b))]);added+=1
  rec.update(total=len(A),new=new);start=sel
 elif st=='UNSAT':
  save();open('/mnt/data/semantic6_FOUND.json','w').write(json.dumps(rec,indent=2));print(json.dumps(rec),flush=True);emit(rec);break
 else:
  print(json.dumps(rec),flush=True);emit(rec);break
 json.dump({'sel':sel.tolist()},open(STATE,'w'))
 emit(rec)
 if added%25==0: save(); print(json.dumps({'checkpoint':len(A),'it':it,'elapsed':time.time()-tall}),flush=True)
else:save()
print(json.dumps({'done':True,'pairs':len(A),'added':added,'elapsed':time.time()-tall}),flush=True)
