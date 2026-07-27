import json,sys,time,os
sys.path.insert(0,'/mnt/data'); import distforge_robust as C
TRACE='/mnt/data/distforge_trace.json'; P=C.P;Q=C.Q;N=C.N

def load(): return json.load(open(TRACE))
def save(D):
 p=TRACE+'.tmp'; json.dump(D,open(p,'w')); os.replace(p,TRACE)

def build(D):
 A=D['alphas'];B=D['betas'];m=len(A); ALL=(1<<m)-1
 feats=[]; cov=[]
 for side,port in [('A',P),('B',Q)]:
  for v in range(N):
   if v in (P,Q): continue
   z=0
   for i,(a,b) in enumerate(zip(A,B)):
    if ((a[port]==a[v]) != (b[port]==b[v])): z |= 1<<i
   feats.append((side,v));cov.append(z)
 return feats,cov,ALL

def compatible(f,g):
 # only forbidden: same control vertex used on both sides
 return not (f[1]==g[1] and f[0]!=g[0]) and f!=g

def find_min3(D):
 feats,cov,ALL=build(D); n=len(feats)
 order=sorted(range(n),key=lambda i:cov[i].bit_count(),reverse=True)
 # 1
 for i in order:
  if cov[i]==ALL:return [i],feats,cov
 # 2 exact
 for aa,ii in enumerate(order):
  ci=cov[ii]
  for jj in order[aa+1:]:
   if compatible(feats[ii],feats[jj]) and (ci|cov[jj])==ALL:return [ii,jj],feats,cov
 # 3 exact-ish, sorted; use a witness uncovered bit and only features covering it
 coverers=[[] for _ in range(len(D['alphas']))]
 for h in order:
  x=cov[h]
  while x:
   l=x & -x; j=l.bit_length()-1; coverers[j].append(h); x-=l
 for aa,ii in enumerate(order):
  ci=cov[ii]
  for jj in order[aa+1:]:
   if not compatible(feats[ii],feats[jj]):continue
   u=ALL^(ci|cov[jj])
   if not u:return [ii,jj],feats,cov
   j=(u & -u).bit_length()-1
   for hh in coverers[j]:
    if hh==ii or hh==jj:continue
    if compatible(feats[ii],feats[hh]) and compatible(feats[jj],feats[hh]) and ((ci|cov[jj]|cov[hh])==ALL):
     return [ii,jj,hh],feats,cov
 return None,feats,cov

def main(iters=100,oracle_t=10):
 for it in range(iters):
  D=load(); t=time.time(); idx,feats,cov=find_min3(D); sec=time.time()-t
  if idx is None:
   print('NO_COVER_LE3 pairs',len(D['alphas']),'sec',sec,flush=True);break
  fs=[feats[i] for i in idx]; atoms=[(P,v) if s=='A' else (Q,v) for s,v in fs]
  st,a,b,osec,size=C.oracle_atoms(atoms,800000+len(D['iterations']),oracle_t)
  rec={'phase':'star-bitset','pairs':len(D['alphas']),'features':fs,'nfeatures':len(fs),'master_sec':sec,'status':st,'oracle_sec':osec}
  if st=='SAT': rec['new_pair']=C.dedup(D,a,b)
  D['iterations'].append(rec);save(D);print(it,rec,flush=True)
  if st!='SAT':break
if __name__=='__main__':main(*(int(x) for x in sys.argv[1:]))
