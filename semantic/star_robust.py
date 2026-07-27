import json,numpy as np,time,os,sys
sys.path.insert(0,'/mnt/data');import distforge_robust as C
TRACE='/mnt/data/distforge_trace.json';P=C.P;Q=C.Q;N=C.N
def save(D):
 D.pop('_seen',None);tmp=TRACE+'.tmp';json.dump(D,open(tmp,'w'));os.replace(tmp,TRACE)
def star_cover(alphas,betas,tries=30):
 A=np.asarray(alphas,dtype=np.int8);B=np.asarray(betas,dtype=np.int8);m=len(A)
 dA=((A==A[:,[P]])!=(B==B[:,[P]]));dB=((A==A[:,[Q]])!=(B==B[:,[Q]]))
 valid=np.ones(N,bool);valid[[P,Q]]=False;best=None
 for seed in range(tries):
  rng=np.random.default_rng(seed+99991*m);unc=np.ones(m,bool);sa=[];sb=[];ua=set();ub=set()
  while unc.any():
   x=dA[unc].sum(0).astype(int);y=dB[unc].sum(0).astype(int);x[~valid]=-1;y[~valid]=-1
   if ub:x[list(ub)]=-1
   if ua:y[list(ua)]=-1
   if ua:x[list(ua)]=-1
   if ub:y[list(ub)]=-1
   mx=max(int(x.max()),int(y.max()))
   if mx<=0:sa=sb=None;break
   opts=[('A',int(v)) for v in np.flatnonzero(x==mx)]+[('B',int(v)) for v in np.flatnonzero(y==mx)]
   side,v=opts[rng.integers(len(opts))]
   if side=='A':sa.append(v);ua.add(v);unc&=~dA[:,v]
   else:sb.append(v);ub.add(v);unc&=~dB[:,v]
  if sa is not None:
   key=(len(sa)+len(sb),max(len(sa),len(sb)))
   if best is None or key<best[0]:best=(key,sa,sb)
 return None if best is None else (best[1],best[2])
def main(n=200,limit=5):
 D=json.load(open(TRACE));seq=sum(1 for r in D.get('iterations',[]) if r.get('phase')=='star-robust')
 for j in range(n):
  t=time.time();cv=star_cover(D['alphas'],D['betas'])
  if cv is None:st='DICTIONARY_LIMIT';rec={'phase':'star-robust','seq':seq+j,'pairs':len(D['alphas']),'status':st};D['iterations'].append(rec);save(D);print(rec);break
  sa,sb=cv;atoms=[(P,a) for a in sa]+[(Q,b) for b in sb];st,a,b,sec,size=C.oracle_atoms(atoms,seq+j,limit)
  rec={'phase':'star-robust','seq':seq+j,'pairs':len(D['alphas']),'nfeatures':len(atoms),'Acontrols':sa,'Bcontrols':sb,'status':st,'oracle_sec':sec}
  if st=='SAT':rec['new_pair']=C.dedup(D,a,b)
  D['iterations'].append(rec);save(D)
  if j%10==0 or st!='SAT':print(rec,flush=True)
  if st!='SAT':break
if __name__=='__main__':main(int(sys.argv[1]) if len(sys.argv)>1 else 200,int(sys.argv[2]) if len(sys.argv)>2 else 5)
