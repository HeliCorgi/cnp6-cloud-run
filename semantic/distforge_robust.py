import numpy as np, subprocess,time,os
P=197;Q=387;N=393;K=5;BASE=N*K
SOLVER='/mnt/data/cdcl_sound'
def read_cnf(path):
 n=0;cs=[]
 for line in open(path):
  if line.startswith('p'):n=int(line.split()[2])
  elif line and line[0] not in 'c%0\n':
   c=[int(x) for x in line.split() if x!='0']
   if c:cs.append(c)
 return n,cs
_,AC=read_cnf('/mnt/data/A.cnf');_,BC=read_cnf('/mnt/data/B.cnf')
def shift(c,off):return [(abs(l)+off)*(1 if l>0 else -1) for l in c]
def xv(copy,v,c):return copy*BASE+v*K+c+1
def add_status(cs,copy,u,v,e):
 for c in range(K):
  a=xv(copy,u,c);b=xv(copy,v,c)
  cs.append([-e,-a,b]);cs.append([-e,a,-b]);cs.append([e,-a,-b])
def build_atoms(atoms,path):
 cs=list(AC)+[shift(c,BASE) for c in BC];nv=2*BASE
 for u,v in atoms:
  nv+=1;add_status(cs,0,u,v,nv);add_status(cs,1,u,v,nv)
 with open(path,'w') as f:
  f.write(f'p cnf {nv} {len(cs)}\n')
  for c in cs:f.write(' '.join(map(str,c))+' 0\n')
 return nv,len(cs)
def parse_model(path,nv):
 vals=np.zeros(nv,dtype=np.int8);ok=False
 if not os.path.exists(path):return None
 for line in open(path):
  if line.startswith('v'):
   ok=True
   for s in line.split()[1:]:
    l=int(s)
    if l and abs(l)<=nv:vals[abs(l)-1]=1 if l>0 else 0
 if not ok:return None
 out=[]
 for cp in range(2):
  col=[];off=cp*BASE
  for v in range(N):
   z=np.flatnonzero(vals[off+v*K:off+(v+1)*K])
   if len(z)!=1:return None
   col.append(int(z[0]))
  out.append(col)
 return out
def oracle_atoms(atoms,seq,limit=5):
 path=f'/tmp/robust_{seq}.cnf';out=path+'.model';err=path+'.err';nv,nc=build_atoms(atoms,path)
 t=time.time()
 with open(err,'w') as fe:
  p=subprocess.run([SOLVER,path,out,str(limit)],stdout=subprocess.DEVNULL,stderr=fe)
 sec=time.time()-t
 if p.returncode==20:return 'UNSAT',None,None,sec,(nv,nc)
 if p.returncode==10:
  m=parse_model(out,nv)
  if m is None:return 'UNKNOWN',None,None,sec,(nv,nc)
  a,b=m
  for u,v in atoms:assert ((a[u]==a[v])==(b[u]==b[v]))
  return 'SAT',a,b,sec,(nv,nc)
 return 'UNKNOWN',None,None,sec,(nv,nc)
def canon(x):
 mp={};n=0;o=[]
 for c in x:
  if c not in mp:mp[c]=n;n+=1
  o.append(mp[c])
 return tuple(o)
def dedup(D,a,b):
 key=(canon(a),canon(b))
 # maintain cache if present
 cache=D.setdefault('_seen',None)
 if cache is None:
  ss={(canon(x),canon(y)) for x,y in zip(D['alphas'],D['betas'])};D['_seen']=[list(k[0])+[-1]+list(k[1]) for k in []]
 else:ss={(canon(x),canon(y)) for x,y in zip(D['alphas'],D['betas'])}
 if key in ss:return False
 D['alphas'].append(a);D['betas'].append(b);D.setdefault('sources',[]).append('robust');return True
