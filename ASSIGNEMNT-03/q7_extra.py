import sys,json,numpy as np; sys.path.insert(0,'.')
from manet import *
def agg(rs):
    return {k:float(np.mean([r[k] for r in rs])) for k in ("pdr","delay","first","ctl_pk","nrl")}
o={}
for P in (2,5,15): o[f"DSDV_P{P}"]=agg([simulate("DSDV",40,10,seed=s,area=1200.0,opts={"P":P}) for s in range(1,11)])
o["AODV"]=agg([simulate("AODV",40,10,seed=s,area=1200.0) for s in range(1,11)])
json.dump(o,open("../res_q7x.json","w"),indent=1)
for k,v in o.items(): print(k,{a:round(b,3) for a,b in v.items()})
