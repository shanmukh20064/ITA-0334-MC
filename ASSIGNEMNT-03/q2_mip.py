"""Q2/Q4/Q7: Mobile IP handoff Monte Carlo. One-way delays (ms) are ASSUMPTIONS stated in the report."""
import numpy as np, json
D=dict(mn_fa=5.0,fa_ha=40.0,cn_ha=30.0,cn_fa=45.0,fa_fa=20.0,ha_proc=2.0,l2=100.0)
ADV_PERIOD=1000.0        # agent advertisement period (ms)
def window(variant,rng):
    """ms during which packets sent by CN are lost or stranded after the MN leaves the old FA"""
    adv=rng.uniform(0,ADV_PERIOD)
    if variant=="basic":        # wait for next advertisement, register with HA, HA updates binding
        return D["l2"]+adv+D["mn_fa"]+D["fa_ha"]+D["ha_proc"]
    if variant=="trigger":      # link-layer trigger + agent solicitation (about 10 ms)
        return D["l2"]+10.0+D["mn_fa"]+D["fa_ha"]+D["ha_proc"]
    if variant=="smooth":       # anticipated handoff: old FA buffers, new FA tells old FA, old FA forwards
        return D["l2"]               # only the L2 gap is a real outage; buffered packets are delayed, not lost
    if variant=="ro":           # route optimisation: HA must also update the CN binding (extra CN_HA)
        return D["l2"]+10.0+D["mn_fa"]+D["fa_ha"]+D["ha_proc"]+D["cn_ha"]
def run(variant,T,session=600.0,rate=50,payload=160,runs=200,seed=21,dwell_random=False):
    rng=np.random.default_rng(seed); res=[]
    for _ in range(runs):
        nho=int(session/T); lost=0; delayed=0; wins=[]
        for h in range(nho):
            w=window(variant,rng); wins.append(w)
            lost+=rate*w/1000.0 if variant!="smooth" else rate*D["l2"]/1000.0
            if variant=="smooth": delayed+=rate*(D["l2"]+D["mn_fa"]+D["fa_fa"])/1000.0
        res.append((nho,lost,delayed,np.mean(wins) if wins else 0,np.max(wins) if wins else 0))
    a=np.mean(res,axis=0); total=rate*session
    # delays (ms) : triangular route CN->HA->FA->MN ; RO direct CN->FA->MN
    dl=D["cn_ha"]+D["fa_ha"]+D["mn_fa"] if variant!="ro" else D["cn_fa"]+D["mn_fa"]
    return dict(variant=variant,T=T,handoffs=a[0],lost=a[1],loss_pct=100*a[1]/total,delayed=a[2],mean_window=a[3],max_window=a[4],one_way_ms=dl,
                disrupted_pct=100*a[0]*a[3]/1000.0/session)
if __name__=="__main__":
    out={"delays":D,"dwell":[],"paths":{}}
    for T in (60,30,10,5,2,1):
        for v in ("basic","trigger","smooth","ro"): out["dwell"].append(run(v,T))
    for r in out["dwell"]: print({k:(round(x,2) if isinstance(x,float) else x) for k,x in r.items()})
    # overhead
    ov={}
    for pl in (20,160,512,1400):
        base=pl+8+20 +(12 if pl in(20,160) else 0)      # payload + UDP + IP (+RTP for voice-like)
        ov[pl]=dict(pkt=base,tunnel=base+20,pct=100*20/base,min_encap=100*12/base)
    out["overhead"]=ov
    # registration load at the Home Agent: users x handoff rate
    out["ha_load"]=[dict(users=u,T=T,regs_per_s=u/T,msgs_per_s=4*u/T) for u in (100,1000,10000) for T in (60,10,2)]
    # triangular routing penalty
    out["tri"]=dict(tri=D["cn_ha"]+D["fa_ha"]+D["mn_fa"],direct=D["cn_fa"]+D["mn_fa"])
    # registration latency components
    out["reg"]=dict(request=D["mn_fa"]+D["fa_ha"]+D["ha_proc"],reply=D["fa_ha"]+D["mn_fa"],total=D["mn_fa"]+D["fa_ha"]+D["ha_proc"]+D["fa_ha"]+D["mn_fa"])
    json.dump(out,open("../res_q2.json","w"),indent=1)
    print(out["overhead"],out["tri"],out["reg"])
