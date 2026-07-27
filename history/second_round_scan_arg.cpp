#include <bits/stdc++.h>
using namespace std;
struct P{double x,y;};
struct Key{long long x,y; bool operator==(Key const&o)const{return x==o.x&&y==o.y;}};
struct KH{size_t operator()(Key const&k)const{return std::hash<long long>()(k.x*1000003LL+k.y);}};
Key key(P a){return {llround(a.x*1e8),llround(a.y*1e8)};}
double dist(P a,P b){return hypot(a.x-b.x,a.y-b.y);}
int main(int argc,char**argv){
 string cp=argc>1?argv[1]:"/mnt/data/mp_coords.txt", colp=argc>2?argv[2]:"/mnt/data/macro_pair_all_5.colors", outp=argc>3?argv[3]:"/mnt/data/second_round_killers.txt"; ifstream fc(cp), fm("/mnt/data/mp_macro.txt"), fcol(colp);
 int n,m;fc>>n; vector<P>C(n);for(auto &p:C)fc>>p.x>>p.y;fm>>m;vector<P>M(m);for(auto&p:M)fm>>p.x>>p.y;vector<int> col(n);for(int&i:col)fcol>>i;
 unordered_map<Key,int,KH> idx;idx.reserve(n*2);for(int i=0;i<n;i++)idx[key(C[i])]=i;
 // grid for unit-neighbor lookup
 double cell=1.05; unordered_map<long long,vector<int>> grid; auto gkey=[&](int a,int b){return ((long long)a<<32)^(unsigned)b;};
 for(int i=0;i<n;i++)grid[gkey((int)floor(C[i].x/cell),(int)floor(C[i].y/cell))].push_back(i);
 // macro pair groups rounded distance 1e-8, unit edges
 map<long long,vector<pair<int,int>>> groups; vector<pair<int,int>> U;
 for(int i=0;i<m;i++)for(int j=i+1;j<m;j++){double d=dist(M[i],M[j]);groups[llround(d*1e8)].push_back({i,j});if(fabs(d-1)<3e-7)U.push_back({i,j});}
 unordered_set<string> seen; long long trans=0,ov3=0; int killers=0; map<int,long long> hist;
 ofstream out(outp);
 auto extendable=[&](vector<P> const&A, vector<int> const&old)->bool{
   vector<int> newid(m,-1), news; for(int i=0;i<m;i++)if(old[i]<0){newid[i]=news.size();news.push_back(i);} int q=news.size();
   if(q==0)return true;
   vector<int> mask(q,31); vector<vector<int>> adj(q);
   // old-neighbor prohibitions for each new transformed point
   for(int aa=0;aa<q;aa++){int i=news[aa]; P z=A[i]; int bx=floor(z.x/cell),by=floor(z.y/cell);int forb=0;
     for(int dx=-1;dx<=1;dx++)for(int dy=-1;dy<=1;dy++){auto it=grid.find(gkey(bx+dx,by+dy));if(it==grid.end())continue;for(int v:it->second)if(fabs(dist(z,C[v])-1)<3e-7)forb|=1<<col[v];}
     mask[aa]&=~forb;if(!mask[aa])return false;
   }
   for(auto [i,j]:U){int a=newid[i],b=newid[j];if(a>=0&&b>=0){adj[a].push_back(b);adj[b].push_back(a);}else if(a>=0){mask[a]&=~(1<<col[old[j]]);}else if(b>=0){mask[b]&=~(1<<col[old[i]]);}else if(col[old[i]]==col[old[j]])return false;}
   for(int a=0;a<q;a++)if(!mask[a])return false;
   vector<int> as(q,-1);
   function<bool(int)> dfs=[&](int left){if(!left)return true;int best=-1,bm=0,bc=99;for(int a=0;a<q;a++)if(as[a]<0){int mm=mask[a];for(int b:adj[a])if(as[b]>=0)mm&=~(1<<as[b]);int c=__builtin_popcount((unsigned)mm);if(c<bc){bc=c;best=a;bm=mm;if(c<=1)break;}}if(!bm)return false;while(bm){int bit=bm&-bm;bm-=bit;as[best]=__builtin_ctz((unsigned)bit);if(dfs(left-1))return true;as[best]=-1;}return false;};
   return dfs(q);
 };
 // target all pairs; only distance classes present in macro
 for(int u=0;u<n;u++)for(int v=u+1;v<n;v++){
   long long dk=llround(dist(C[u],C[v])*1e8);auto git=groups.find(dk);if(git==groups.end())continue;
   for(auto [si,sj]:git->second)for(int rev=0;rev<2;rev++)for(int ref=0;ref<2;ref++){
     int tu=rev?v:u,tv=rev?u:v; double ax=M[sj].x-M[si].x, ay=M[sj].y-M[si].y;if(ref)ay=-ay;double bx=C[tv].x-C[tu].x,by=C[tv].y-C[tu].y;double den=ax*ax+ay*ay;double cr=(bx*ax+by*ay)/den, ci=(by*ax-bx*ay)/den;
     vector<P>A(m);vector<int>old(m,-1);string sig;sig.reserve(300);int ov=0;
     for(int k=0;k<m;k++){double x=M[k].x-M[si].x,y=M[k].y-M[si].y;if(ref)y=-y;A[k]={C[tu].x+cr*x-ci*y,C[tu].y+ci*x+cr*y};auto it=idx.find(key(A[k]));if(it!=idx.end()&&dist(A[k],C[it->second])<4e-7){old[k]=it->second;ov++;}auto kk=key(A[k]);sig+=to_string(kk.x)+","+to_string(kk.y)+";";}
     trans++;if(ov<3)continue;if(!seen.insert(sig).second)continue;ov3++;hist[ov]++;
     if(!extendable(A,old)){
       killers++;out<<"K "<<ov;for(int k=0;k<m;k++)out<<" "<<setprecision(17)<<A[k].x<<" "<<A[k].y;out<<"\n";out.flush();cerr<<"killer "<<killers<<" ov="<<ov<<" trans="<<trans<<" unique="<<ov3<<"\n";if(killers>=200)goto done;
     }
   }
 }
 done: cerr<<"done trans="<<trans<<" uniqueov3="<<ov3<<" killers="<<killers<<"\n";for(auto [k,x]:hist)cerr<<"ov"<<k<<"="<<x<<" ";cerr<<"\n";
}
