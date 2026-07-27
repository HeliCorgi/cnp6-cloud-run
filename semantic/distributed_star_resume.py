import json,numpy as np,time,sys,subprocess,os
sys.path.insert(0,'/mnt/data')
import distributed_coupled_resume as C
TRACE=C.TRACE;P=C.P;Q=C.Q;N=C.N

def star_cover(alphas,betas,tries=100):
 A=np.asarray(alphas,dtype=np.int8);B=np.asarray(betas,dtype=np.int8);m=len(A)
 dA=((A==A[:,[P]])!=(B==B[:,[P]]))
 dB=((A==A[:,[Q]])!=(B==B[:,[Q]]))
 valid=np.ones(N,dtype=bool);valid[[P,Q]]=False
 best=None
 for seed in range(tries):
  rng=np.random.default_rng(seed+99991*m);unc=np.ones(m,dtype=bool);sa=[];sb=[];usedA=set();usedB=set()
  while unc.any():
   scA=dA[unc].sum(axis=0).astype(int);scB=dB[unc].sum(axis=0).astype(int)
   scA[~valid]=-1;scB[~valid]=-1
   if usedB:scA[list(usedB)]=-1
   if usedA:scB[list(usedA)]=-1
   if usedA:scA[list(usedA)]=-1
   if usedB:scB[list(usedB)]=-1
   mx=max(int(scA.max()),int(scB.max()))
   if mx<=0:sa=sb=None;break
   opts=[]
   opts += [('A',int(x)) for x in np.flatnonzero(scA==mx)]
   opts += [('B',int(x)) for x in np.flatnonzero(scB==mx)]
   side,v=opts[rng.integers(len(opts))]
   if side=='A':sa.append(v);usedA.add(v);unc &= ~dA[:,v]
   else:sb.append(v);usedB.add(v);unc &= ~dB[:,v]
  if sa is not None:
   key=(len(sa)+len(sb),max(len(sa),len(sb)),len(set(sa+sb)))
   if best is None or key<best[0]:best=(key,sa,sb)
 return None if best is None else (best[1],best[2])

def build_atoms(sa,sb):return [(P,a) for a in sa]+[(Q,b) for b in sb]
def oracle_atoms(sa,sb,seq,limit=60):
 atoms=build_atoms(sa,sb)
 # use C internals but build directly
 cs=list(C.AC)+[C.shift(c,C.BASE) for c in C.BC];nv=2*C.BASE
 for u,v in atoms:
  nv+=1;C.add_status(cs,0,u,v,nv);C.add_status(cs,1,u,v,nv)
 path=f'/tmp/dstar_{seq}.cnf';out=path+'.out';err=path+'.err'
 with open(path,'w') as f:
  f.write(f'p cnf {nv} {len(cs)}\n');
  for c in cs:f.write(' '.join(map(str,c))+' 0\n')
 t=time.time()
 try:
  with open(out,'w') as fo,open(err,'w') as fe:p=subprocess.run([C.SOLVER,path],stdout=fo,stderr=fe,timeout=limit)
 except subprocess.TimeoutExpired:return 'UNKNOWN',None,None,time.time()-t,(nv,len(cs))
 if p.returncode==20:return 'UNSAT',None,None,time.time()-t,(nv,len(cs))
 if p.returncode==10:
  mm=C.parse_model(out,nv)
  if mm is None:return 'UNKNOWN',None,None,time.time()-t,(nv,len(cs))
  a,b=mm
  for u,v in atoms:assert ((a[u]==a[v])==(b[u]==b[v]))
  return 'SAT',a,b,time.time()-t,(nv,len(cs))
 return 'UNKNOWN',None,None,time.time()-t,(nv,len(cs))

def main(maxit=100,limit=60):
 D=json.load(open(TRACE));seq=max([r.get('star_seq',-1) for r in D.get('iterations',[])]+[-1])+1
 for j in range(maxit):
  t=time.time();cv=star_cover(D['alphas'],D['betas'],tries=20)
  if cv is None:
   rec={'phase':'coupled-star','star_seq':seq+j,'pairs':len(D['alphas']),'status':'DICTIONARY_LIMIT'};D['iterations'].append(rec);json.dump(D,open(TRACE,'w'));print(json.dumps(rec));break
  sa,sb=cv;st,a,b,sec,size=oracle_atoms(sa,sb,seq+j,limit)
  rec={'phase':'coupled-star','star_seq':seq+j,'pairs':len(D['alphas']),'nfeatures':len(sa)+len(sb),'Acontrols':sa,'Bcontrols':sb,'status':st,'oracle_sec':sec,'total_sec':time.time()-t,'cnf':size}
  if st=='SAT':rec['new_pair']=C.dedup_pair(D,a,b)
  D['iterations'].append(rec);json.dump(D,open(TRACE,'w'));print(json.dumps(rec),flush=True)
  if st!='SAT':break
if __name__=='__main__':main(int(sys.argv[1]) if len(sys.argv)>1 else 100,int(sys.argv[2]) if len(sys.argv)>2 else 60)
