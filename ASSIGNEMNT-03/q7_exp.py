import sys,json,time,numpy as np; sys.path.insert(0,'.')
from manet import *
def agg(rs,keys=("pdr","pdr_before","pdr_after","delay","delay95","first","avail","ctl_pk","ctl_by","nrl")):
    d={}
    for k in keys:
        v=np.array([r[k] for r in rs],float); v=v[~np.isnan(v)]
        d[k]=float(v.mean()) if len(v) else float("nan"); d[k+"_sd"]=float(v.std(ddof=1)) if len(v)>1 else 0.0
    d["n"]=len(rs); return d
SEEDS=range(1,11); AREA=1200.0; out={}; t0=time.time()
kw=dict(area=AREA)
out["size"]={f"{p}_{N}":agg([simulate(p,N,10,seed=s,**kw) for s in SEEDS]) for N in (10,20,40,80) for p in ("DSDV","AODV")}; print("size",time.time()-t0,flush=True)
out["speed"]={f"{p}_{v}":agg([simulate(p,40,v,seed=s,**kw) for s in SEEDS]) for v in (2,10,20,30) for p in ("DSDV","AODV")}; print("speed",time.time()-t0,flush=True)
out["fail"]={"DSDV":agg([simulate("DSDV",40,10,seed=s,fail_frac=0.3,fail_at=100,**kw) for s in SEEDS]),
             "AODV":agg([simulate("AODV",40,10,seed=s,fail_frac=0.3,fail_at=100,**kw) for s in SEEDS]),
             "AODV+buffer":agg([simulate("AODV",40,10,seed=s,fail_frac=0.3,fail_at=100,opts={"buffer":60},**kw) for s in SEEDS])}; print("fail",time.time()-t0,flush=True)
out["discon"]={"AODV":agg([simulate("AODV",12,10,seed=s,**kw) for s in SEEDS]),"AODV+buffer":agg([simulate("AODV",12,10,seed=s,opts={"buffer":60},**kw) for s in SEEDS]),
               "DSDV":agg([simulate("DSDV",12,10,seed=s,**kw) for s in SEEDS])}
json.dump(out,open("../res_q7.json","w"),indent=1); print("done",time.time()-t0)
