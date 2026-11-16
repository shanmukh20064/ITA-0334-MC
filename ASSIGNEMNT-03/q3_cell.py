"""Q3: cellular vs ad hoc under infrastructure failure; handoff rate; scalability. Seeded Monte Carlo."""
import numpy as np, json, math
from manet import adjacency, bfs
AREA=2000.0
BS=np.array([[x,y] for x in (333,1000,1667) for y in (333,1000,1667)],float)   # 3x3 base stations
RB=500.0; RA=250.0
def cellular(N,f,rng):
    u=rng.uniform(0,AREA,(N,2)); alive=rng.random(len(BS))>f
    d=np.linalg.norm(u[:,None,:]-BS[None],axis=2); d[:,~alive]=1e9
    cov=(d.min(axis=1)<=RB)
    # two users can talk if both are covered (core assumed reachable from every surviving BS)
    k=cov.sum(); return k*(k-1)/(N*(N-1))
def adhoc(N,f,rng,R=RA):
    p=rng.uniform(0,AREA,(N,2)); alive=rng.random(N)>f
    A=adjacency(p,R); A[~alive,:]=False; A[:,~alive]=False
    idx=np.nonzero(alive)[0]; comp={}; c=0; lab=np.full(N,-1)
    for i in idx:
        if lab[i]<0:
            d,_=bfs(A,i); lab[d>=0]=c; c+=1
    sizes=np.bincount(lab[idx],minlength=c) if c else np.array([0])
    tot=N*(N-1); conn=(sizes*(sizes-1)).sum()
    # mean hop count between connected pairs
    hops=[]
    for i in idx[:12]:
        d,_=bfs(A,i); hops+= [x for x in d if x>0]
    return conn/tot, (np.mean(hops) if hops else float("nan"))
def handoffs(v,rng,T=3600.0,dt=1.0):
    pos=rng.uniform(300,1700,2); ang=rng.uniform(0,2*math.pi); cur=None; n=0
    for _ in range(int(T/dt)):
        pos=pos+v*dt*np.array([math.cos(ang),math.sin(ang)])
        if not(0<pos[0]<AREA and 0<pos[1]<AREA): ang+=math.pi; pos=np.clip(pos,1,AREA-1)
        b=int(np.argmin(np.linalg.norm(BS-pos,axis=1)))
        if cur is not None and b!=cur: n+=1
        cur=b
    return n
if __name__=="__main__":
    rng=np.random.default_rng(31); out={}
    fs=[0,0.1,0.2,0.3,0.5,0.7,0.9]
    out["fail"]=[]
    for f in fs:
        cel=np.mean([cellular(100,f,rng) for _ in range(200)])
        ah=[adhoc(100,f,rng) for _ in range(40)]
        out["fail"].append(dict(f=f,cellular=float(cel),adhoc=float(np.mean([a[0] for a in ah])),hops=float(np.nanmean([a[1] for a in ah]))))
    out["density"]=[]
    for N in (20,40,60,100,150,200):
        ah=[adhoc(N,0.0,rng) for _ in range(40)]; ah3=[adhoc(N,0.3,rng) for _ in range(40)]
        out["density"].append(dict(N=N,conn=float(np.mean([a[0] for a in ah])),conn30=float(np.mean([a[0] for a in ah3])),hops=float(np.nanmean([a[1] for a in ah]))))
    out["handoff"]=[]
    R=math.sqrt((AREA/3)**2/math.pi)
    for v in (1.4,13.9,27.8):
        h=np.mean([handoffs(v,np.random.default_rng(40+i)) for i in range(6)])
        out["handoff"].append(dict(v=v,sim_per_hour=float(h),formula=2*v/(math.pi*R)*3600))
    # scalability: per-user throughput (Mbps).  cellular: C=20 Mbps per cell shared by users in cell, 9 cells
    out["scale"]=[]
    for n in (10,50,100,200,500,1000):
        cel=20.0/max(1,n/9.0); w=11.0; ah=w/math.sqrt(n*math.log(n)) if n>1 else w     # Gupta-Kumar order of growth, constant 1 (assumption)
        out["scale"].append(dict(n=n,cellular=min(cel,20.0),adhoc=ah))
    json.dump(out,open("../res_q3.json","w"),indent=1)
    for k in out: 
        for r in out[k]: print(k,{a:round(b,3) for a,b in r.items()})
