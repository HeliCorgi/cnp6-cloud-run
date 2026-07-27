import sys,os,time,subprocess,json
import numpy as np
sys.path.insert(0,'/mnt/data');import distforge_robust as C
P=C.P;Q=C.Q;N=C.N;K=C.K;BASE=C.BASE
VALID=[v for v in range(N) if v not in (P,Q)]

def shift(cl,off): return [(abs(x)+off)*(1 if x>0 else -1) for x in cl]
def xv(cp,v,c): return cp*BASE+v*K+c+1

def add_eq_status(cs,cp,u,v,e):
    for c in range(K):
        a=xv(cp,u,c); b=xv(cp,v,c)
        cs.append([-e,-a,b]);cs.append([-e,a,-b]);cs.append([e,-a,-b])

def add_xnor(cs,a,b,m):
    cs.append([-a,-b,m]);cs.append([a,b,m]);cs.append([-a,b,-m]);cs.append([a,-b,-m])

def parse_full(path,nv):
    vals=np.zeros(nv+1,dtype=np.int8);ok=False
    if not os.path.exists(path):return None
    for line in open(path):
        if line.startswith('v'):
            ok=True
            for s in line.split()[1:]:
                z=int(s)
                if z and abs(z)<=nv: vals[abs(z)]=1 if z>0 else 0
    return vals if ok else None

def colors(vals):
    out=[]
    for cp in range(2):
        col=[]
        for v in range(N):
            z=[c for c in range(K) if vals[xv(cp,v,c)]]
            if len(z)!=1:return None
            col.append(z[0])
        out.append(col)
    return out

def build(candidate_atoms):
    cs=list(C.AC)+[shift(cl,BASE) for cl in C.BC]; nv=2*BASE
    obs=[]; match=[]
    for center in (P,Q):
        for v in VALID:
            nv+=1;e0=nv;add_eq_status(cs,0,center,v,e0)
            nv+=1;e1=nv;add_eq_status(cs,1,center,v,e1)
            nv+=1;m=nv;add_xnor(cs,e0,e1,m)
            obs.append((center,v));match.append(m)
    index={o:i for i,o in enumerate(obs)}
    for o in candidate_atoms:cs.append([match[index[tuple(o)]]])
    return cs,nv,obs,match

def enumerate_signatures(candidate_atoms,nmodels=100,limit=20,seq=0):
    cs,nv,obs,match=build(candidate_atoms);res=[];t0=time.time()
    for j in range(nmodels):
        path=f'/tmp/sig_{seq}_{j}.cnf';out=path+'.model'
        with open(path,'w') as f:
            f.write(f'p cnf {nv} {len(cs)}\n')
            for cl in cs:f.write(' '.join(map(str,cl))+' 0\n')
        p=subprocess.run([C.SOLVER,path,out,str(limit)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if p.returncode!=10: return res,time.time()-t0,('UNSAT' if p.returncode==20 else 'UNKNOWN')
        vals=parse_full(out,nv);cc=colors(vals)
        if cc is None:return res,time.time()-t0,'BADMODEL'
        a,b=cc
        sig=[]
        for center,v in obs:sig.append((a[center]==a[v])==(b[center]==b[v]))
        # verify match variables and block this exact signature
        for bit,m in zip(sig,match):
            if bool(vals[m])!=bool(bit):raise RuntimeError('match mismatch')
        cs.append([(-m if bit else m) for bit,m in zip(sig,match)])
        res.append((a,b,sig))
    return res,time.time()-t0,'LIMIT'
if __name__=='__main__':
    atoms=[tuple(map(int,x.split(','))) for x in sys.argv[1].split(';')]
    rr,sec,st=enumerate_signatures(atoms,int(sys.argv[2]),int(sys.argv[3]),int(time.time()))
    print(json.dumps({'n':len(rr),'sec':sec,'status':st,'unique_sigs':len({tuple(r[2]) for r in rr})}))
