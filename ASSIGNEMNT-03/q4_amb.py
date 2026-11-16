"""Q4: ambulance-to-hospital telemedicine over cellular with Mobile IP. 24 km route at 60 km/h."""
import numpy as np, json
from q2_mip import window, D
V=16.7; L=24000.0; T=L/V
TOWERS=[2000+4000*i for i in range(6)]           # cell centres (m), radius 2.5 km
DEAD=[(9500,9900),(17300,17700)]                  # two 400 m coverage holes
RATE_V=10; RATE_A=50                              # vitals pps (uplink), voice pps (downlink)
def run(variant,backup,seed):
    rng=np.random.default_rng(seed); 
    boundaries=[(TOWERS[i]+TOWERS[i+1])/2/V for i in range(5)]
    wins=[window(variant,rng) for _ in boundaries]
    outage=[(b,w/1000.0) for b,w in zip(boundaries,wins)]
    dz=[((a/V),(b-a)/V) for a,b in DEAD]
    out_total=sum(w for _,w in outage); dz_total=sum(d for _,d in dz)
    if backup: dz=[(s,2.0) for s,_ in dz]           # fall back to a second link after 2 s detection
    gaps=[w for _,w in outage]+[d for _,d in dz]
    lost_v=RATE_V*(sum(w for _,w in outage)+sum(d for _,d in dz))
    lost_a=RATE_A*(sum(w for _,w in outage)+sum(d for _,d in dz))
    # on-time delivery: reverse tunnel both ways (ingress filtering) -> 90 ms nominal, +-10 ms jitter; backup link adds 40 ms
    up=rng.normal(20+D["fa_ha"]+D["cn_ha"],10,int(RATE_V*T)); dn=rng.normal(D["cn_ha"]+D["fa_ha"]+20,10,int(RATE_A*T))
    late_v=(up>150).mean(); late_a=(dn>150).mean()
    return dict(handoff_out=out_total,dead_out=sum(d for _,d in dz),max_gap=max(gaps),loss_v=100*lost_v/(RATE_V*T),loss_a=100*lost_a/(RATE_A*T),late_v=100*late_v,late_a=100*late_a,
                up_ms=float(up.mean()),dn_ms=float(dn.mean()),gaps_gt2=sum(1 for g in gaps if g>2.0))
if __name__=="__main__":
    out={"T":T,"cfg":[]}
    for variant,backup,name in (("basic",False,"Basic Mobile IP"),("trigger",False,"+ link-layer trigger"),("smooth",False,"+ smooth handoff (buffering)"),("smooth",True,"+ smooth handoff + backup link")):
        rs=[run(variant,backup,s) for s in range(100)]
        out["cfg"].append(dict(name=name,**{k:float(np.mean([r[k] for r in rs])) for k in rs[0]}))
    json.dump(out,open("../res_q4.json","w"),indent=1)
    for c in out["cfg"]: print({k:(round(v,2) if isinstance(v,float) else v) for k,v in c.items()})
