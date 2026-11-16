"""Q1: mobile user driving through 3 access points. Seeded Monte Carlo, time step 20 ms (20 packets/s)."""
import numpy as np, json, math
DT=0.05; SENS=-85.0
def rssi_model(d,n=2.7): return -20-10*n*np.log10(np.maximum(d,1.0))
def trip(v,rng,S=400.0,H=4.0,Th=0.10,others=3,hys_on=True,log=False,cap=2e6,ap_x=None):
    ap=np.array(ap_x if ap_x is not None else [0,S,2*S],float)
    x0=-100.0; x1=ap[-1]+100.0; T=(x1-x0)/v; n=int(T/DT)
    # correlated shadowing per AP (Gudmundson, decorrelation 20 m, sigma 3 dB)
    rho=math.exp(-v*DT/20.0); sh=rng.normal(0,3,len(ap))
    cur=-1; ho_end=-1.0; hos=0; pingpong=0; last_from=None; last_ho_t=-99
    lam_o=others*25.0; mu=cap/8000.0           # pkts/s (1000-byte packets, 25 pps per other user)
    lam=lam_o+20.0; rho_q=lam/mu
    qdelay=1.0/(mu-lam) if rho_q<1 else 0.5; qloss=max(0.0,1-1.0/rho_q) if rho_q>=1 else 0.0
    sent=ok=late=0; delays=[]; last_ok=0.0; gaps=[]; down=0.0; ev=[]
    for k in range(n):
        t=k*DT; x=x0+v*t
        sh=rho*sh+math.sqrt(1-rho*rho)*rng.normal(0,3,len(ap))
        r=rssi_model(np.abs(x-ap))+sh
        if t>=ho_end:
            best=int(np.argmax(r))
            if cur<0:
                if r[best]>=SENS:
                    cur=best; ho_end=t+Th; hos+=1
                    if log: ev.append((round(t,2),f"attach to AP{best+1} (RSSI {r[best]:.0f} dBm), scan+auth {Th*1000:.0f} ms"))
            else:
                trig=(r[best]>r[cur]+(H if hys_on else 0.0)) and best!=cur
                if trig or r[cur]<SENS and r[best]>=SENS and best!=cur:
                    if last_from==best and t-last_ho_t<5.0: pingpong+=1
                    last_from=cur; last_ho_t=t
                    if log: ev.append((round(t,2),f"handoff AP{cur+1}->AP{best+1}: RSSI {r[cur]:.0f} vs {r[best]:.0f} dBm, link down {Th*1000:.0f} ms"))
                    cur=best; ho_end=t+Th; hos+=1
        if k%1==0:                                        # one packet per 50 ms
            sent+=1
            if cur<0 or t<ho_end: success=False
            else:
                p_loss=1/(1+math.exp((r[cur]+84.0)/1.2)); success=(rng.random()>p_loss) and (rng.random()>qloss)
            if success:
                dl=0.005+qdelay*(0.5+rng.random()); delays.append(dl)
                if dl<=0.1: ok+=1
                if t-last_ok>0.2: gaps.append(t-last_ok)
                last_ok=t
            else: down+=DT
    return dict(T=T,sent=sent,ok=ok,pdr=ok/sent,delay=float(np.mean(delays)) if delays else float("nan"),handoffs=hos,pingpong=pingpong,
                gaps=len(gaps),longest=max(gaps) if gaps else 0.0,down=down,events=ev)
def agg(f,runs=30,seed=11,**kw):
    rs=[f(rng=np.random.default_rng(seed+i),**kw) for i in range(runs)]
    m=lambda k:float(np.mean([r[k] for r in rs])); 
    return dict(v=kw.get("v"),pdr=m("pdr"),delay=m("delay")*1000,handoffs=m("handoffs"),pingpong=m("pingpong"),gaps=m("gaps"),longest=m("longest"),down=m("down"),T=m("T"))
if __name__=="__main__":
    out={}
    out["speed"]=[agg(trip,v=v) for v in (2,5,10,20,30)]
    out["hys"]=[dict(H=H,**agg(trip,v=10,H=H)) for H in (0,2,4,8)]
    out["spacing"]=[dict(S=S,**agg(trip,v=10,S=S)) for S in (400,500,600,700)]
    out["load"]=[dict(others=o,**agg(trip,v=10,others=o)) for o in (0,3,6,8,9,10)]
    out["events"]=trip(10,np.random.default_rng(5),log=True)["events"]
    # analytic cross-check: expected handoff rate
    json.dump(out,open("../res_q1.json","w"),indent=1)
    for k in ("speed","hys","spacing","load"):
        for r in out[k]: print(k,{a:round(b,2) for a,b in r.items()})
    print(out["events"])
