#include <bits/stdc++.h>
using namespace std;
struct AP{int cnt,a,c;};
int main(){
 ifstream f("/mnt/data/aaab.bin",ios::binary); uint32_t M,N;f.read((char*)&M,4);f.read((char*)&N,4);
 vector<uint8_t> AA((size_t)M*N),AB((size_t)M*N);f.read((char*)AA.data(),AA.size());f.read((char*)AB.data(),AB.size());
 vector<int> V;for(int i=0;i<(int)N;i++)if(i!=197&&i!=387)V.push_back(i);
 vector<AP> aps;aps.reserve(V.size()*(V.size()+1)/2);
 for(int ii=0;ii<(int)V.size();ii++)for(int jj=ii;jj<(int)V.size();jj++){
   int a=V[ii],c=V[jj],cnt=0;for(int r=0;r<(int)M;r++)cnt+=AA[(size_t)r*N+a]&AA[(size_t)r*N+c];
   aps.push_back({cnt,a,c});
 }
 sort(aps.begin(),aps.end(),[](auto &x,auto &y){if(x.cnt!=y.cnt)return x.cnt<y.cnt;if(x.a!=y.a)return x.a<y.a;return x.c<y.c;});
 cerr<<"M "<<M<<" AP "<<aps.size()<<" min "<<aps[0].cnt<<"\n";
 auto st=chrono::steady_clock::now();
 for(size_t rank=0;rank<aps.size();rank++){
   auto [cnt,a,c]=aps[rank]; vector<int> rows;rows.reserve(cnt);
   for(int r=0;r<(int)M;r++)if(AA[(size_t)r*N+a]&AA[(size_t)r*N+c])rows.push_back(r);
   int W=(rows.size()+63)/64; vector<uint64_t> masks((size_t)V.size()*W);
   for(int bi=0;bi<(int)V.size();bi++){
     int b=V[bi]; if(b==a||b==c)continue;
     for(int k=0;k<(int)rows.size();k++)if(AB[(size_t)rows[k]*N+b])masks[(size_t)bi*W+k/64]|=1ULL<<(k%64);
   }
   for(int bi=0;bi<(int)V.size();bi++){
     int b=V[bi];if(b==a||b==c)continue;
     for(int di=bi;di<(int)V.size();di++){
       int d=V[di];if(d==a||d==c)continue;bool ok=true;
       for(int w=0;w<W;w++)if(masks[(size_t)bi*W+w]&masks[(size_t)di*W+w]){ok=false;break;}
       if(ok){
         cout<<a<<" "<<c<<" "<<b<<" "<<d<<" "<<cnt<<" "<<rank<<"\n";return 0;
       }
     }
   }
   if(rank%5000==0){double s=chrono::duration<double>(chrono::steady_clock::now()-st).count();cerr<<"rank "<<rank<<" cnt "<<cnt<<" sec "<<s<<"\n";}
 }
 cout<<"NONE\n";
}
