import numpy as np, scipy.sparse as sp
from scipy.optimize import milp,LinearConstraint,Bounds
import sys,os,json,time,itertools
sys.path.insert(0,'/mnt/data');import distforge_robust as R
from local6_utils import local_find,canon
NPZ='/mnt/data/distforge_pairs.npz';STATE='/mnt/data/local6_state.json';LOG='/mnt/data/local6_hybrid.jsonl';P=R.P;Q=R.Q;N=R.N
valid=np.array([v for v in range(N) if v not in (P,Q)],dtype=np.int32);L=len(valid)
rng=np.random.default_rng(26072611)
z=np.load(NPZ);A=z['alphas'].copy();B=z['betas'].copy()
def rowD(a,b):
 p=((a[valid]==a[P])==(b[valid]==b[P]));q=((a[valid]==a[Q])==(b[valid]==b[Q]));return np.concatenate([~p,~q])
def allD(A,B):
 p=((A[:,valid]==A[:,[P]])==(B[:,valid]==B[:,[P]]));q=((A[:,valid]==A[:,[Q]])==(B[:,valid]==B[:,[Q]]));return np.concatenate([~p,~q],axis=1)
D=allD(A,B);seen={(canon(x),canon(y)) for x,y in zip(A,B)}
def reducible(sel):
 for pi in itertools.combinations(sel[:3],2):
  for qi in itertools.combinations(sel[3:],2):
   if np.all(D[:,list(pi)+list(qi)].any(axis=1)):return True
 return False
def exact_find(limit=30):
 S=sp.csr_matrix(D.astype(np.int8));M=len(D)
 base=LinearConstraint(S,np.ones(M),np.full(M,np.inf))
 rp=np.zeros(2*L);rp[:L]=1;rq=np.zeros(2*L);rq[L:]=1
 count=LinearConstraint(np.vstack([rp,rq]),[3,3],[3,3]);cuts=[]
 for inner in range(30):
  cons=[base,count]
  if cuts:
   rows=[]
   for cut in cuts:
    r=np.zeros(2*L);r[cut]=1;rows.append(r)
   cons.append(LinearConstraint(sp.csr_matrix(np.vstack(rows)),np.full(len(rows),-np.inf),np.full(len(rows),3)))
  c=1e-6*rng.random(2*L)
  res=milp(c,integrality=np.ones(2*L),bounds=Bounds(0,1),constraints=cons,options={'time_limit':limit,'mip_rel_gap':0})
  if res.x is None:return None,{'status':int(res.status),'msg':res.message,'inner':inner}
  sel=np.flatnonzero(res.x>.5).astype(int)
  if len(sel)!=6:return None,{'status':'badlen','len':len(sel)}
  sel=np.r_[np.sort(sel[sel<L]),np.sort(sel[sel>=L])]
  bad=[]
  for pi in itertools.combinations(sel[:3],2):
   for qi in itertools.combinations(sel[3:],2):
    cols=list(pi)+list(qi)
    if np.all(D[:,cols].any(axis=1)):bad.append(cols)
  if not bad:return sel,{'inner':inner,'cuts':len(cuts),'optimal':bool(res.success)}
  old={tuple(sorted(x)) for x in cuts}
  for x in bad:old.add(tuple(sorted(x)))
  cuts=[list(x) for x in old]
 return None,{'status':'cutlimit'}
def atoms(sel):return [(P,int(valid[x])) for x in sel[:3]]+[(Q,int(valid[x-L])) for x in sel[3:]]
def save():
 t=NPZ+'.tmp.npz';np.savez(t,alphas=A,betas=B);os.replace(t,NPZ)
def log(rec):
 with open(LOG,'a') as f:f.write(json.dumps(rec)+'\n')
start=None
if os.path.exists(STATE):
 try:start=np.array(json.load(open(STATE))['sel'],int)
 except:pass
iters=int(sys.argv[1]) if len(sys.argv)>1 else 500;added=0;tall=time.time();fallbacks=0
for it in range(iters):
 t=time.time();sel,sc=local_find(D,start,restarts=2,steps=12);mode='local';meta={'best':sc}
 if sel is None:
  mode='exact';fallbacks+=1;sel,meta=exact_find(35)
 if sel is None:
  rec={'it':it,'pairs':len(A),'master':'NONE_OR_UNKNOWN','mode':mode,'meta':meta,'elapsed':time.time()-tall};log(rec);print(json.dumps(rec),flush=True);save();break
 at=atoms(sel);st,a,b,sec,cnf=R.oracle_atoms(at,9500000+len(A)+it,limit=30)
 rec={'it':it,'pairs_before':len(A),'mode':mode,'meta':meta,'sel':sel.tolist(),'atoms':at,'oracle':st,'oracle_sec':sec,'master_sec':time.time()-t-sec}
 if st=='SAT':
  k=(canon(a),canon(b));new=k not in seen
  if new:
   seen.add(k);A=np.vstack([A,np.asarray(a,np.uint8)]);B=np.vstack([B,np.asarray(b,np.uint8)]);D=np.vstack([D,rowD(np.asarray(a),np.asarray(b))]);added+=1
  rec.update(total=len(A),new=new);start=sel
 elif st=='UNSAT':
  save();open('/mnt/data/semantic6_FOUND.json','w').write(json.dumps(rec,indent=2));log(rec);print(json.dumps(rec),flush=True);break
 else:
  save();log(rec);print(json.dumps(rec),flush=True);break
 json.dump({'sel':sel.tolist()},open(STATE,'w'));log(rec)
 if added%25==0:
  save();print(json.dumps({'checkpoint':len(A),'it':it,'fallbacks':fallbacks,'elapsed':time.time()-tall}),flush=True)
else:save()
print(json.dumps({'done':True,'pairs':len(A),'added':added,'fallbacks':fallbacks,'elapsed':time.time()-tall}),flush=True)
