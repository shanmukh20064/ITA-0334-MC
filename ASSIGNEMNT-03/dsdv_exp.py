import sys,json,numpy as np; sys.path.insert(0,'.')
from manet import *
NAMES="ABCDEF"
def table(P,i,names=NAMES):
    rows=[]
    for d in range(P.N):
        m=P.met[i,d]; rows.append([names[d],names[P.nh[i,d]] if P.nh[i,d]>=0 and d!=i else ("-" if d==i else "-"),"inf" if m>=INF else int(m),int(P.seq[i,d])])
    return rows
def converge(P,A,maxr=30):
    r=0
    while r<maxr:
        before=(P.met.copy(),P.nh.copy())
        for u in range(P.N): P._bcast(u,A,True)
        r+=1
        # drain triggered updates produced
        while P.changed.any(): 
            for u in np.nonzero(P.changed.any(axis=1))[0]: P._bcast(u,A,False)
        if (P.met<INF).all(): break
    return r
def demo():
    N=6; A=np.zeros((N,N),bool)
    for a,b in [(0,1),(1,2),(2,3),(1,4),(4,3),(4,5)]: A[a,b]=A[b,a]=True
    P=DSDV(N,np.random.default_rng(1),P=1e9)
    r=converge(P,A); out={"edges":[(NAMES[a]+NAMES[b]) for a in range(N) for b in range(a+1,N) if A[a,b]],"rounds":r,"tx_conv":P.ctl.tot()}
    out["A_before"]=table(P,0); out["E_before"]=table(P,4)
    # break link B-E (1-4)
    A2=A.copy(); A2[1,4]=A2[4,1]=False; tx0=P.ctl.tot()
    P.last=A.copy(); rounds=P.step(1,A2)          # detection + triggered updates
    out["A_after_trigger"]=table(P,0); out["B_after_trigger"]=table(P,1); out["trig_rounds"]=rounds; out["trig_tx"]=P.ctl.tot()-tx0
    tx1=P.ctl.tot(); r2=0
    while not (P.met<INF).all() and r2<20:   # periodic full dumps from every node (each node increments its own even sequence)
        for u in range(N): P._bcast(u,A2,True)
        while P.changed.any():
            for u in np.nonzero(P.changed.any(axis=1))[0]: P._bcast(u,A2,False)
        r2+=1
    out["periodic_rounds"]=r2; out["periodic_tx"]=P.ctl.tot()-tx1
    out["A_after_converged"]=table(P,0); out["B_after_converged"]=table(P,1)
    return out
def connected(A):
    d,_=bfs(A,0); return (d>=0).all()
def rgg(N,rng,R=250,area=None):
    area=area or 1000*np.sqrt(N/30)*1.0
    while True:
        pos=rng.uniform(0,area,(N,2)); A=adjacency(pos[None][0],R)
        if connected(A): return A
def recovery(N,seed,Pint=15.0):
    rng=np.random.default_rng(seed); A=rgg(N,rng)
    P=DSDV(N,np.random.default_rng(seed+1),P=Pint)
    # warm-up with periodic updates until converged
    t=0
    while not (P.met<INF).all() and t<400: P.step(t,A); t+=1
    conv=t; tx_conv=P.ctl.tot(); t+=1
    # pick an edge on some shortest path whose removal keeps graph connected
    edges=[(a,b) for a in range(N) for b in range(a+1,N) if A[a,b]]
    rng.shuffle(edges)
    for a,b in edges:
        A2=A.copy(); A2[a,b]=A2[b,a]=False
        if connected(A2): break
    tx0=P.ctl.tot(); t_fail=t; P.step(t,A2); t+=1
    broken_after_trig=int((P.met>=INF).sum()); 
    rt=0
    while not (P.met<INF).all() and rt<200: P.step(t,A2); t+=1; rt+=1
    # additional: first time when all routes are valid = rt+1 seconds
    return dict(N=N,conv_s=conv,tx_conv=tx_conv,broken=broken_after_trig,recover_s=rt+1,tx_rec=P.ctl.tot()-tx0)
if __name__=="__main__":
    res={"demo":demo(),"rec":{}}
    for N in (10,20,50):
        rs=[recovery(N,s) for s in range(1,21)]
        res["rec"][N]={k:float(np.mean([r[k] for r in rs])) for k in rs[0]}; res["rec"][N]["recover_max"]=max(r["recover_s"] for r in rs)
        print(N,res["rec"][N],flush=True)
    json.dump(res,open("../res_dsdv.json","w"),indent=1)
    d=res["demo"]; print(d["A_before"]); print(d["A_after_trigger"]); print(d["A_after_converged"]); print(d["trig_rounds"],d["trig_tx"],d["periodic_rounds"],d["periodic_tx"],d["rounds"],d["tx_conv"])
