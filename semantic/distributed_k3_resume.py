import json,numpy as np,time,sys
sys.path.insert(0,'/mnt/data')
import distributed_coupled_resume as C
TRACE=C.TRACE;P=C.P;Q=C.Q;N=C.N

def cover_k3(alphas,betas,tries=8,target=2):
 A=np.asarray(alphas,dtype=np.int8);B=np.asarray(betas,dtype=np.int8);m=len(A)
 agA=((A==A[:,[P]])==(B==B[:,[P]])); agB=((A==A[:,[Q]])==(B==B[:,[Q]]))
 mask=np.ones((N,N),dtype=bool)
 for x in (P,Q):mask[x,:]=False;mask[:,x]=False
 np.fill_diagonal(mask,False)
 best=None;bestkey=None
 # total coverage tie score precompute
 totalcov=m-agA.astype(np.int16).T@agB.astype(np.int16)
 totalcov[~mask]=-1
 for seed in range(tries):
  rng=np.random.default_rng(seed+1000003*m); counts=np.zeros(m,dtype=np.int8); sh=[];ua=set();ub=set()
  for step in range(3):
   active=counts<target
   if active.any():
    aa=agA[active].astype(np.int16);bb=agB[active].astype(np.int16)
    score=int(active.sum())-aa.T@bb
   else: score=totalcov.copy()
   score=score.astype(np.int64)*(m+1)+totalcov
   score[~mask]=-1
   if ub:score[sorted(ub),:]=-1
   if ua:score[:,sorted(ua)]=-1
   for a,b in sh:score[a,b]=-1
   mx=int(score.max())
   if mx<0:sh=None;break
   cand=np.argwhere(score==mx);a,b=map(int,cand[rng.integers(len(cand))]);sh.append((a,b));ua.add(a);ub.add(b)
   counts += (~(agA[:,a]&agB[:,b])).astype(np.int8)
  if sh is None:continue
  key=(int(counts.min()),int((counts>=2).sum()),int(counts.sum()),int((counts==3).sum()))
  if bestkey is None or key>bestkey:bestkey=key;best=sh
 return best,bestkey

def main(maxit=50,limit=30):
 D=json.load(open(TRACE)); seq=max([r.get('k3_seq',-1) for r in D.get('iterations',[])]+[-1])+1
 for j in range(maxit):
  t=time.time();sh,key=cover_k3(D['alphas'],D['betas'])
  st,a,b,sec,size,atoms=C.oracle(sh,100000+seq+j,limit)
  rec={'phase':'coupled-k3','k3_seq':seq+j,'pairs':len(D['alphas']),'nshapes':3,'shapes':sh,'cover_key':key,'natoms':len(atoms),'status':st,'oracle_sec':sec,'total_sec':time.time()-t,'cnf':size}
  if st=='SAT':rec['new_pair']=C.dedup_pair(D,a,b)
  D['iterations'].append(rec);json.dump(D,open(TRACE,'w'));print(json.dumps(rec),flush=True)
  if st!='SAT':break
if __name__=='__main__':main(int(sys.argv[1]) if len(sys.argv)>1 else 50,int(sys.argv[2]) if len(sys.argv)>2 else 30)
