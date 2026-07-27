import ctypes,time,json
from pathlib import Path
lib=ctypes.CDLL('/lib/x86_64-linux-gnu/libz3.so.4');V=ctypes.c_void_p;U=ctypes.c_uint;B=ctypes.c_bool
# sig helper
def sig(n,args,rest=None): f=getattr(lib,n);f.argtypes=args;f.restype=rest;return f
mkcfg=sig('Z3_mk_config',[],V);delcfg=sig('Z3_del_config',[V]);mkctx=sig('Z3_mk_context',[V],V);delctx=sig('Z3_del_context',[V]);mksolver=sig('Z3_mk_solver',[V],V);sinc=sig('Z3_solver_inc_ref',[V,V]);sdec=sig('Z3_solver_dec_ref',[V,V]);mksym=sig('Z3_mk_string_symbol',[V,ctypes.c_char_p],V);mkbs=sig('Z3_mk_bool_sort',[V],V);mkconst=sig('Z3_mk_const',[V,V,V],V);mknot=sig('Z3_mk_not',[V,V],V);mkor=sig('Z3_mk_or',[V,U,ctypes.POINTER(V)],V);ass=sig('Z3_solver_assert',[V,V,V]);check=sig('Z3_solver_check',[V,V],ctypes.c_int);push=sig('Z3_solver_push',[V,V]);pop=sig('Z3_solver_pop',[V,V,U]);getm=sig('Z3_solver_get_model',[V,V],V);minc=sig('Z3_model_inc_ref',[V,V]);mdec=sig('Z3_model_dec_ref',[V,V]);meval=sig('Z3_model_eval',[V,V,V,B,ctypes.POINTER(V)],B);gbv=sig('Z3_get_bool_value',[V,V],ctypes.c_int);mkp=sig('Z3_mk_params',[V],V);pinc=sig('Z3_params_inc_ref',[V,V]);pdec=sig('Z3_params_dec_ref',[V,V]);psu=sig('Z3_params_set_uint',[V,V,V,U]);sset=sig('Z3_solver_set_params',[V,V,V])
cnf='/mnt/data/macro_cegis_6_case10.cnf'
n=0;cls=[]
for line in open(cnf):
 if not line.strip() or line[0] in 'c%':continue
 if line.startswith('p '):n=int(line.split()[2]);continue
 cl=[int(x) for x in line.split() if int(x)!=0]
 if cl:cls.append(cl)
base=cls[:-7]
G=json.load(open('/mnt/data/macro_cegis_6.json'));vs=[2,7,8,9,12,14,15];E={tuple(sorted(e)) for e in G['edges']};adj={(i,j) for i in range(7) for j in range(i+1,7) if tuple(sorted((vs[i],vs[j]))) in E}
cases=[]
def rec(a):
 i=len(a)
 if i==7:cases.append(tuple(a));return
 mx=max(a,default=-1)
 for c in range(min(mx+1,4)+1):
  if all((j,i) not in adj or a[j]!=c for j in range(i)):rec(a+[c])
rec([])
print('cases',len(cases),'base clauses',len(base),flush=True)
cfg=mkcfg();ctx=mkctx(cfg);delcfg(cfg);s=mksolver(ctx);sinc(ctx,s);bs=mkbs(ctx);xs=[None]+[mkconst(ctx,mksym(ctx,f'x{i}'.encode()),bs) for i in range(1,n+1)]
def ast(cl):
 arr=(V*len(cl))(*[(xs[x] if x>0 else mknot(ctx,xs[-x])) for x in cl]);return arr[0] if len(cl)==1 else mkor(ctx,len(cl),arr)
t=time.time()
for j,cl in enumerate(base):ass(ctx,s,ast(cl))
print('assert',time.time()-t,flush=True)
p=mkp(ctx);pinc(ctx,p);psu(ctx,p,mksym(ctx,b'timeout'),10000);sset(ctx,s,p);pdec(ctx,p)
import sys
lo=int(sys.argv[1]); hi=int(sys.argv[2])
for ci in range(lo,hi):
 colors=cases[ci]
 push(ctx,s)
 for v,c in zip(vs,colors):ass(ctx,s,xs[5*v+c+1])
 t=time.time();r=check(ctx,s);dt=time.time()-t
 print(ci,colors,{1:'SAT',0:'UNK',-1:'UNSAT'}[r],round(dt,3),flush=True)
 if r==1:
  m=getm(ctx,s);minc(ctx,m);vals=[]
  for i in range(1,n+1):
   o=V();meval(ctx,m,xs[i],True,ctypes.byref(o));vals.append(str(i if gbv(ctx,o)==1 else -i))
  Path(f'/mnt/data/macro_cegis_6_case{ci:02d}.model').write_text('s SATISFIABLE\nv '+' '.join(vals)+' 0\n');mdec(ctx,m)
  print('FOUND',ci,flush=True);break
 pop(ctx,s,1)
sdec(ctx,s);delctx(ctx)
