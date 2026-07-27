import json, numpy as np, subprocess, time, os, sys
P=197; Q=387; N=393; K=5; BASE=N*K
TRACE='/mnt/data/distributed_disjoint_trace.json'
SOLVER='/mnt/data/cdcl_sound'

def read_cnf(path):
 n=0; cs=[]
 for line in open(path):
  if line.startswith('p'): n=int(line.split()[2])
  elif line and line[0] not in 'c%0\n':
   c=[int(x) for x in line.split() if x!='0']
   if c:cs.append(c)
 return n,cs
_,AC=read_cnf('/mnt/data/A.cnf'); _,BC=read_cnf('/mnt/data/B.cnf')
def shift(c,off):return [(abs(l)+off)*(1 if l>0 else -1) for l in c]
def xv(copy,v,c):return copy*BASE+v*K+c+1
def add_status(cs,copy,u,v,e):
 for c in range(K):
  a=xv(copy,u,c);b=xv(copy,v,c)
  cs.append([-e,-a,b]);cs.append([-e,a,-b]);cs.append([e,-a,-b])
def build(shapes,path):
 cs=list(AC)+[shift(c,BASE) for c in BC]; nv=2*BASE
 atoms=[]
 for a,b in shapes:
  for z in ((P,a),(Q,b)):
   if z not in atoms:atoms.append(z)
 for u,v in atoms:
  nv+=1; add_status(cs,0,u,v,nv); add_status(cs,1,u,v,nv)
 with open(path,'w') as f:
  f.write(f'p cnf {nv} {len(cs)}\n')
  for c in cs:f.write(' '.join(map(str,c))+' 0\n')
 return nv,len(cs),atoms
def parse_model(path,nv):
 lits=[]
 for line in open(path):
  if line.startswith('v'):lits += [int(x) for x in line.split()[1:] if x!='0']
 if not lits:return None
 vals=np.zeros(nv,dtype=np.int8)
 for l in lits:
  if abs(l)<=nv:vals[abs(l)-1]=1 if l>0 else 0
 out=[]
 for cp in range(2):
  col=[];off=cp*BASE
  for v in range(N):
   z=np.flatnonzero(vals[off+v*K:off+(v+1)*K])
   if len(z)!=1:return None
   col.append(int(z[0]))
  out.append(col)
 return out
def oracle(shapes,seq,limit=60):
 path=f'/tmp/dcoupled_{seq}.cnf';out=path+'.out';err=path+'.err';nv,nc,atoms=build(shapes,path)
 t=time.time()
 try:
  with open(out,'w') as fo,open(err,'w') as fe:
   p=subprocess.run([SOLVER,path],stdout=fo,stderr=fe,timeout=limit)
 except subprocess.TimeoutExpired:
  return 'UNKNOWN',None,None,time.time()-t,(nv,nc),atoms
 if p.returncode==20:return 'UNSAT',None,None,time.time()-t,(nv,nc),atoms
 if p.returncode==10:
  m=parse_model(out,nv)
  if m is None:return 'UNKNOWN',None,None,time.time()-t,(nv,nc),atoms
  a,b=m
  # exact oracle invariant
  for x,y in shapes:
   assert ((a[P]==a[x])==(b[P]==b[x]))
   assert ((a[Q]==a[y])==(b[Q]==b[y]))
  return 'SAT',a,b,time.time()-t,(nv,nc),atoms
 return 'UNKNOWN',None,None,time.time()-t,(nv,nc),atoms

def cover(alphas,betas,tries=12):
 A=np.asarray(alphas,dtype=np.int8);B=np.asarray(betas,dtype=np.int8);m=len(A)
 agreeA=((A==A[:,[P]])==(B==B[:,[P]]));agreeB=((A==A[:,[Q]])==(B==B[:,[Q]]))
 mask=np.ones((N,N),dtype=bool)
 for x in (P,Q):mask[x,:]=False;mask[:,x]=False
 np.fill_diagonal(mask,False)
 best=None
 for seed in range(tries):
  rng=np.random.default_rng(seed+104729*m);unc=np.ones(m,dtype=bool);sh=[];ua=set();ub=set()
  while unc.any():
   aa=agreeA[unc].astype(np.int16);bb=agreeB[unc].astype(np.int16)
   cov=int(unc.sum())-aa.T@bb;cov[~mask]=-1
   if ub:cov[sorted(ub),:]=-1
   if ua:cov[:,sorted(ua)]=-1
   for a,b in sh:cov[a,b]=-1
   mx=int(cov.max())
   if mx<=0:sh=None;break
   cand=np.argwhere(cov==mx);a,b=map(int,cand[rng.integers(len(cand))]);sh.append((a,b));ua.add(a);ub.add(b)
   unc &= (agreeA[:,a]&agreeB[:,b])
  if sh is not None and (best is None or len(sh)<len(best)):best=sh
 return best

def dedup_pair(D,a,b):
 # Exact color names can differ. Canonicalize each model independently by first occurrence, then compare pair.
 def canon(x):
  mp={};n=0;o=[]
  for c in x:
   if c not in mp:mp[c]=n;n+=1
   o.append(mp[c])
  return tuple(o)
 ca,cb=canon(a),canon(b)
 for x,y in zip(D['alphas'],D['betas']):
  if canon(x)==ca and canon(y)==cb:return False
 D['alphas'].append(a);D['betas'].append(b);return True

def main(maxit=100,limit=60):
 D=json.load(open(TRACE));seq=max([r.get('coupled_seq',-1) for r in D.get('iterations',[])]+[-1])+1
 for j in range(maxit):
  t=time.time();sh=cover(D['alphas'],D['betas'])
  if sh is None:
   rec={'phase':'coupled','coupled_seq':seq+j,'pairs':len(D['alphas']),'status':'DICTIONARY_LIMIT'}
   D['iterations'].append(rec);json.dump(D,open(TRACE,'w'));print(json.dumps(rec),flush=True);break
  st,a,b,sec,size,atoms=oracle(sh,seq+j,limit)
  rec={'phase':'coupled','coupled_seq':seq+j,'pairs':len(D['alphas']),'nshapes':len(sh),'shapes':sh,'natoms':len(atoms),'status':st,'oracle_sec':sec,'total_sec':time.time()-t,'cnf':size}
  if st=='SAT':rec['new_pair']=dedup_pair(D,a,b)
  D['iterations'].append(rec);json.dump(D,open(TRACE,'w'));print(json.dumps(rec),flush=True)
  if st!='SAT':break
if __name__=='__main__':main(int(sys.argv[1]) if len(sys.argv)>1 else 100,int(sys.argv[2]) if len(sys.argv)>2 else 60)
