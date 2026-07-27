import numpy as np, scipy.sparse as sp
from scipy.optimize import milp, LinearConstraint, Bounds
import itertools, json, time, sys
NPZ='/mnt/data/distforge_pairs.npz'; P=197;Q=387;N=393
z=np.load(NPZ);A=z['alphas'];B=z['betas'];M=len(A)
valid=[v for v in range(N) if v not in (P,Q)]
# columns: P-v then Q-v
agP=((A[:,valid]==A[:,[P]])==(B[:,valid]==B[:,[P]]))
agQ=((A[:,valid]==A[:,[Q]])==(B[:,valid]==B[:,[Q]]))
D=np.concatenate([~agP,~agQ],axis=1).astype(np.int8)
# sparse row constraints sum D*x >= 1
S=sp.csr_matrix(D)
base=LinearConstraint(S, np.ones(M), np.full(M,np.inf))
# exact 3 on each side
rowP=np.zeros(2*len(valid));rowP[:len(valid)]=1
rowQ=np.zeros(2*len(valid));rowQ[len(valid):]=1
count=LinearConstraint(np.vstack([rowP,rowQ]),[3,3],[3,3])
cuts=[]
rng=np.random.default_rng(20260726)
def atoms_from_x(x):
 inds=np.flatnonzero(x>.5)
 pp=[valid[i] for i in inds if i<len(valid)]
 qq=[valid[i-len(valid)] for i in inds if i>=len(valid)]
 return pp,qq,inds.tolist()
def is_cover(cols):
 return np.all(D[:,cols].any(axis=1))
for it in range(200):
 cons=[base,count]
 if cuts:
  rows=[]
  for cut in cuts:
   r=np.zeros(2*len(valid));r[cut]=1;rows.append(r)
  cons.append(LinearConstraint(sp.csr_matrix(np.vstack(rows)),np.full(len(rows),-np.inf),np.full(len(rows),3)))
 c=1e-6*rng.random(2*len(valid))
 t=time.time();res=milp(c,integrality=np.ones(2*len(valid)),bounds=Bounds(0,1),constraints=cons,options={'time_limit':60,'mip_rel_gap':0})
 print(json.dumps({'it':it,'success':bool(res.success),'status':int(res.status),'msg':res.message,'sec':time.time()-t,'cuts':len(cuts)}),flush=True)
 if res.x is None: sys.exit(2)
 pp,qq,inds=atoms_from_x(res.x)
 bad=[]
 for pi in itertools.combinations(range(3),2):
  for qi in itertools.combinations(range(3),2):
   cols=[valid.index(pp[i]) for i in pi]+[len(valid)+valid.index(qq[i]) for i in qi]
   if is_cover(cols):bad.append(cols)
 if not bad:
  out={'P':pp,'Q':qq,'cols':inds,'pairs':M,'cuts':len(cuts)}
  print('FOUND',json.dumps(out),flush=True)
  open('/mnt/data/irredundant6_candidate.json','w').write(json.dumps(out,indent=2))
  break
 # add all bad 4-subsets as cuts
 old={tuple(sorted(x)) for x in cuts}
 for x in bad: old.add(tuple(sorted(x)))
 cuts=[list(x) for x in sorted(old)]
 print('candidate',pp,qq,'bad',len(bad),'cutsnow',len(cuts),flush=True)
else: print('NOFOUND')
