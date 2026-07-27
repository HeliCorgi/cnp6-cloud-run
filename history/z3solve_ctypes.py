import ctypes,sys,time
from pathlib import Path
lib=ctypes.CDLL('/lib/x86_64-linux-gnu/libz3.so.4')
# types
c_void_p=ctypes.c_void_p;c_uint=ctypes.c_uint;c_int=ctypes.c_int;c_char_p=ctypes.c_char_p;c_bool=ctypes.c_bool
# signatures
lib.Z3_mk_config.restype=c_void_p
lib.Z3_del_config.argtypes=[c_void_p]
lib.Z3_mk_context.argtypes=[c_void_p];lib.Z3_mk_context.restype=c_void_p
lib.Z3_del_context.argtypes=[c_void_p]
lib.Z3_mk_solver.argtypes=[c_void_p];lib.Z3_mk_solver.restype=c_void_p
lib.Z3_solver_inc_ref.argtypes=[c_void_p,c_void_p]
lib.Z3_solver_dec_ref.argtypes=[c_void_p,c_void_p]
lib.Z3_mk_string_symbol.argtypes=[c_void_p,c_char_p];lib.Z3_mk_string_symbol.restype=c_void_p
lib.Z3_mk_const.argtypes=[c_void_p,c_void_p,c_void_p];lib.Z3_mk_const.restype=c_void_p
lib.Z3_mk_bool_sort.argtypes=[c_void_p];lib.Z3_mk_bool_sort.restype=c_void_p
lib.Z3_mk_not.argtypes=[c_void_p,c_void_p];lib.Z3_mk_not.restype=c_void_p
lib.Z3_mk_or.argtypes=[c_void_p,c_uint,ctypes.POINTER(c_void_p)];lib.Z3_mk_or.restype=c_void_p
lib.Z3_solver_assert.argtypes=[c_void_p,c_void_p,c_void_p]
lib.Z3_solver_check.argtypes=[c_void_p,c_void_p];lib.Z3_solver_check.restype=c_int
lib.Z3_solver_get_model.argtypes=[c_void_p,c_void_p];lib.Z3_solver_get_model.restype=c_void_p
lib.Z3_model_inc_ref.argtypes=[c_void_p,c_void_p]
lib.Z3_model_dec_ref.argtypes=[c_void_p,c_void_p]
lib.Z3_model_eval.argtypes=[c_void_p,c_void_p,c_void_p,c_bool,ctypes.POINTER(c_void_p)];lib.Z3_model_eval.restype=c_bool
lib.Z3_get_bool_value.argtypes=[c_void_p,c_void_p];lib.Z3_get_bool_value.restype=c_int
lib.Z3_solver_set_params.argtypes=[c_void_p,c_void_p,c_void_p]
lib.Z3_mk_params.argtypes=[c_void_p];lib.Z3_mk_params.restype=c_void_p
lib.Z3_params_inc_ref.argtypes=[c_void_p,c_void_p];lib.Z3_params_dec_ref.argtypes=[c_void_p,c_void_p]
lib.Z3_params_set_uint.argtypes=[c_void_p,c_void_p,c_void_p,c_uint]

def parse(path):
 n=0; clauses=[]
 with open(path) as f:
  cur=[]
  for line in f:
   if not line or line[0] in 'c%0\n': continue
   if line.startswith('p '): n=int(line.split()[2]); continue
   for x in map(int,line.split()):
    if x==0:
     if cur: clauses.append(cur);cur=[]
    else:cur.append(x)
  if cur:clauses.append(cur)
 return n,clauses

def main():
 cnf=sys.argv[1]; out=sys.argv[2] if len(sys.argv)>2 else None; timeout=int(sys.argv[3]) if len(sys.argv)>3 else 0
 n,clauses=parse(cnf); print('parsed',n,len(clauses),flush=True)
 cfg=lib.Z3_mk_config(); ctx=lib.Z3_mk_context(cfg);lib.Z3_del_config(cfg)
 solver=lib.Z3_mk_solver(ctx);lib.Z3_solver_inc_ref(ctx,solver)
 if timeout:
  p=lib.Z3_mk_params(ctx);lib.Z3_params_inc_ref(ctx,p)
  sym=lib.Z3_mk_string_symbol(ctx,b'timeout');lib.Z3_params_set_uint(ctx,p,sym,timeout*1000)
  lib.Z3_solver_set_params(ctx,solver,p);lib.Z3_params_dec_ref(ctx,p)
 bs=lib.Z3_mk_bool_sort(ctx)
 vars=[None]+[lib.Z3_mk_const(ctx,lib.Z3_mk_string_symbol(ctx,f'x{i}'.encode()),bs) for i in range(1,n+1)]
 t=time.time()
 for j,cl in enumerate(clauses):
  arr=(c_void_p*len(cl))()
  for k,l in enumerate(cl): arr[k]=vars[l] if l>0 else lib.Z3_mk_not(ctx,vars[-l])
  a=arr[0] if len(cl)==1 else lib.Z3_mk_or(ctx,len(cl),arr)
  lib.Z3_solver_assert(ctx,solver,a)
  if j and j%50000==0: print('asserted',j,flush=True)
 print('assert time',time.time()-t,flush=True)
 r=lib.Z3_solver_check(ctx,solver); print('result',r,'time',time.time()-t,flush=True)
 lines=[]
 if r==1:
  lines.append('s SATISFIABLE');m=lib.Z3_solver_get_model(ctx,solver);lib.Z3_model_inc_ref(ctx,m)
  vals=[]
  for i in range(1,n+1):
   v=c_void_p();lib.Z3_model_eval(ctx,m,vars[i],True,ctypes.byref(v));bv=lib.Z3_get_bool_value(ctx,v)
   vals.append(str(i if bv==1 else -i))
  lines.append('v '+' '.join(vals)+' 0');lib.Z3_model_dec_ref(ctx,m)
 elif r==-1: lines.append('s UNSATISFIABLE')
 else: lines.append('s UNKNOWN')
 if out:Path(out).write_text('\n'.join(lines)+'\n')
 print(lines[0])
 lib.Z3_solver_dec_ref(ctx,solver);lib.Z3_del_context(ctx)
if __name__=='__main__':main()
