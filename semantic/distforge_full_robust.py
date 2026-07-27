import json,time,os,sys
import numpy as np
sys.path.insert(0,'/mnt/data'); import distforge_robust as C
TRACE='/mnt/data/distforge_trace.json'; STATE='/mnt/data/distforge_full_state.json'; P=C.P;Q=C.Q;N=C.N

def savej(x,p):
 t=p+'.tmp'; json.dump(x,open(t,'w')); os.replace(t,p)

def greedy(D, orbit_weight=0.0):
 A=np.asarray(D['alphas'],dtype=np.int8);B=np.asarray(D['betas'],dtype=np.int8);m=len(A)
 aa=((A==A[:,[P]])==(B==B[:,[P]])).astype(np.int16)
 ab=((A==A[:,[Q]])==(B==B[:,[Q]])).astype(np.int16)
 mask=np.ones((N,N),bool)
 for x in (P,Q):mask[x,:]=False;mask[:,x]=False
 np.fill_diagonal(mask,False)
 uncovered=np.ones(m,bool);chosen=[];ua=set();ub=set()
 while uncovered.any():
  XA=aa[uncovered];XB=ab[uncovered]
  both=XA.T@XB;cov=int(uncovered.sum())-both
  cov[~mask]=-1
  if ua:cov[:,sorted(ua)]=-1
  if ub:cov[sorted(ub),:]=-1
  for a,b in chosen:cov[a,b]=-1
  idx=int(np.argmax(cov));a,b=divmod(idx,N);gain=int(cov[a,b])
  if gain<=0:return None,int(uncovered.sum())
  chosen.append((a,b));ua.add(a);ub.add(b)
  uncovered &= ((aa[:,a]&ab[:,b]) != 0)
 return chosen,0

def main(iters=100,limit=20):
 for it in range(iters):
  D=json.load(open(TRACE)); t=time.time();sh,left=greedy(D);ms=time.time()-t
  if sh is None:
   rec={'status':'DICTIONARY_LIMIT','pairs':len(D['alphas']),'left':left,'master_sec':ms};savej(rec,STATE);print(rec,flush=True);break
  atoms=sorted(set([(P,a) for a,b in sh]+[(Q,b) for a,b in sh]))
  st,a,b,sec,size=C.oracle_atoms(atoms,900000+len(D['iterations']),limit)
  rec={'phase':'full-distributed','pairs':len(D['alphas']),'nshapes':len(sh),'natoms':len(atoms),'shapes':sh,'status':st,'master_sec':ms,'oracle_sec':sec}
  if st=='SAT':rec['new_pair']=C.dedup(D,a,b)
  D['iterations'].append(rec);savej(D,TRACE);savej(rec,STATE);print(it,rec,flush=True)
  if st!='SAT':break
if __name__=='__main__':main(*(int(x) for x in sys.argv[1:]))
