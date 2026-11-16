import sys,json,time,numpy as np; sys.path.insert(0,'.')
from manet import *
out={}
def agg(rs,keys=("pdr","delay","delay95","first","avail","ctl_pk","ctl_by","nrl")):
    d={}
    for k in keys:
        v=np.array([r[k] for r in rs],float); v=v[~np.isnan(v)]
        d[k]=float(v.mean()) if len(v) else float("nan"); d[k+"_sd"]=float(v.std(ddof=1)) if len(v)>1 else 0.0
    d["n"]=len(rs)
    for k in ("disc","disc_fail","disc_lat"):
        if k in rs[0]: d[k]=float(np.nanmean([r[k] for r in rs]))
    d["kinds"]={}
    for r in rs:
        for k,v in r["kinds"].items(): d["kinds"][k]=d["kinds"].get(k,0)+v/len(rs)
    return d
SEEDS=range(1,11)
t0=time.time()
# network size sweep, v=5
out["size"]={}
for N in (10,20,40,80):
    for pr in ("DSDV","AODV"):
        out["size"][f"{pr}_{N}"]=agg([simulate(pr,N,5,seed=s) for s in SEEDS]); print("size",pr,N,round(time.time()-t0),flush=True)
# speed sweep, N=30
out["speed"]={}
for v in (0,1,2,5,10,20):
    for pr in ("DSDV","AODV"):
        out["speed"][f"{pr}_{v}"]=agg([simulate(pr,30,v,seed=s) for s in SEEDS]); print("speed",pr,v,round(time.time()-t0),flush=True)
# DSDV update interval and AODV hello sensitivity, N=30 v=5
out["sens"]={}
for P in (2,5,15,30): out["sens"][f"DSDV_P{P}"]=agg([simulate("DSDV",30,5,seed=s,opts={"P":P}) for s in SEEDS])
out["sens"]["AODV_hello"]=agg([simulate("AODV",30,5,seed=s,opts={"hello":True}) for s in SEEDS])
out["sens"]["AODV_lr"]=agg([simulate("AODV",30,5,seed=s,opts={"lr":True}) for s in SEEDS])
print("sens",round(time.time()-t0),flush=True)
json.dump(out,open("../res_manet.json","w"),indent=1)
