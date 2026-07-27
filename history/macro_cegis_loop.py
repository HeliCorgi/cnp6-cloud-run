import json,subprocess,sys
from pathlib import Path
start_step=int(sys.argv[1]);end_step=int(sys.argv[2]);graph=sys.argv[3];model=sys.argv[4];case=int(sys.argv[5])
def extract_colors(graph,model,out):
 G=json.load(open(graph));n=len(G['coords']);t=Path(model).read_text().split();true={int(x) for x in t if x.lstrip('-').isdigit() and int(x)>0};cols=[]
 for v in range(n):
  cs=[c for c in range(5) if 5*v+c+1 in true]
  if len(cs)!=1:raise RuntimeError((v,cs))
  cols.append(cs[0])
 if any(cols[u]==cols[v] for u,v in G['edges']):raise RuntimeError('bad edge')
 Path(out).write_text('\n'.join(map(str,cols))+'\n')
 return cols
colors=f'/mnt/data/macro_loop_{start_step-1}.colors';extract_colors(graph,model,colors)
for step in range(start_step,end_step+1):
 print('STEP',step,'case',case,'graph',graph,flush=True)
 p=subprocess.run(['python','/mnt/data/cegis_macro_step.py',graph,colors,str(step),str(case)],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,timeout=120)
 print(p.stdout.strip().splitlines()[-1],flush=True)
 ng=f'/mnt/data/macro_cegis_{step}.json';basecnf=f'/mnt/data/macro_cegis_{step}_case{case:02d}.cnf'
 src=Path(basecnf).read_text().splitlines();body=src[1:-7];h=src[0]
 order=[]
 for cc in [case,0,3,4,10]+list(range(42)):
  if cc not in order:order.append(cc)
 solved=False
 for cc in order:
  cnf=f'/mnt/data/macro_cegis_{step}_case{cc:02d}.cnf';mod=f'/mnt/data/macro_cegis_{step}_case{cc:02d}.model';log=f'/mnt/data/macro_cegis_{step}_case{cc:02d}.log'
  if cc!=case or not Path(cnf).exists():
   units=Path(f'/mnt/data/spcases/case{cc:02d}.cnf').read_text().splitlines()[-7:]
   Path(cnf).write_text(h+'\n'+'\n'.join(body+units)+'\n')
  try:r=subprocess.run(['/mnt/data/z3_dimacs',cnf,mod],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=75)
  except subprocess.TimeoutExpired:
   Path(log).write_text('TIMEOUT\n');print(' try',cc,'TIMEOUT',flush=True);continue
  Path(log).write_text(r.stdout)
  status=Path(mod).read_text().splitlines()[0] if Path(mod).exists() else ''
  print(' try',cc,status,flush=True)
  if status.strip()=='s SATISFIABLE':
   graph=ng;model=mod;case=cc;colors=f'/mnt/data/macro_cegis_{step}_5.colors';extract_colors(graph,model,colors);solved=True;break
 if not solved:
  print('NO SAT CASE within limits at step',step,flush=True);sys.exit(3)
print('DONE',graph,model,case,colors)
