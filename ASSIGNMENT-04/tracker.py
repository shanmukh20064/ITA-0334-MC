"""Task 6 (Part II): battery-aware, secure tracking policy. Core logic (policy, energy model) is separate from the scenario/printing code.
Energy constants are ASSUMED (documented power model), not measured."""
import json,math,tracemalloc,time
E_SAMPLE=60.0        # mAs per location+sensor sample (GPS fix + sensor read + CPU)
E_ENC=0.05           # mAs per record, AES-GCM with hardware-backed key
E_UP_FIXED={"WIFI":150.0,"LTE":500.0}   # mAs per upload (radio ramp + tail)
E_UP_REC={"WIFI":0.005,"LTE":0.02}      # mAs per record transferred
REC_BYTES=64; GCM_OVERHEAD=28
def battery_state(pct,charging,saver):
    if charging: return "CHARGING"
    if saver or pct<15: return "CRITICAL"
    if pct<50: return "LOW"
    return "OK"
BASE_INT={"MOVING":10,"STATIONARY":120}
MULT={"CHARGING":1.0,"OK":1.0,"LOW":2.0,"CRITICAL":4.0}
BATCH_AGE={"OK":300,"LOW":900,"CRITICAL":None}     # seconds before an LTE upload is allowed; None = wait for Wi-Fi/charging
QUEUE_LIMIT=5000
MIN_BATCH=10     # never wake the radio for fewer than 10 queued records (found by the validation step: see report)
def policy(pct,charging,saver,net,motion,hot):
    b=battery_state(pct,charging,saver)
    interval=BASE_INT[motion]*MULT[b]*(2.0 if hot else 1.0)
    period=None
    if net=="NONE": up="queue (no connectivity)"
    elif b=="CHARGING" and net=="WIFI": period=interval; up="upload now (flush queue)"
    elif hot: up="defer upload until cool (flush only if queue >= limit)"
    elif b=="CRITICAL": up="defer to charging/Wi-Fi window (flush only if queue >= limit)"
    else:
        base=300 if (net=="WIFI" or b=="OK" or b=="CHARGING") else BATCH_AGE["LOW"]
        period=max(base,MIN_BATCH*interval); up="batch upload every %d min"%round(period/60)
    return b,interval,up,period
def simulate_hour(pct,charging,saver,net,motion,hot,seconds=3600):
    b,interval,up,period=policy(pct,charging,saver,net,motion,hot)
    n=int(seconds//interval)
    wakeups=0 if period is None else int(seconds//period)
    if period is None and net!="NONE" and n>=QUEUE_LIMIT: wakeups=n//QUEUE_LIMIT
    if period is not None: sent=min(n,wakeups*max(1,math.ceil(period/interval)))
    else: sent=(n-n%QUEUE_LIMIT) if (net!="NONE" and n>=QUEUE_LIMIT) else 0
    key="WIFI" if net=="WIFI" else "LTE"
    e_up=(wakeups*E_UP_FIXED[key]+sent*E_UP_REC[key]) if net!="NONE" else 0.0
    e=n*(E_SAMPLE+E_ENC)+e_up
    return dict(battery=b,interval_s=interval,upload=up,period_s=period,records=n,sent=sent,queued=n-sent,wakeups=wakeups,energy_mAh=round(e/3600,3),
                encrypted_at_rest=True,encrypted_in_transit=(net!="NONE" and sent>0),useful_per_mAh=round(sent/(e/3600),1) if e>0 and sent else 0.0)
SCEN=[("1  Charging on Wi-Fi, moving",dict(pct=60,charging=True,saver=False,net="WIFI",motion="MOVING",hot=False)),
("2  80% battery, LTE, moving",dict(pct=80,charging=False,saver=False,net="LTE",motion="MOVING",hot=False)),
("3  20% battery, LTE, stationary",dict(pct=20,charging=False,saver=False,net="LTE",motion="STATIONARY",hot=False)),
("4  14% battery, battery-saver on, LTE, moving",dict(pct=14,charging=False,saver=True,net="LTE",motion="MOVING",hot=False)),
("5  60% battery, no connectivity, moving",dict(pct=60,charging=False,saver=False,net="NONE",motion="MOVING",hot=False)),
("6  70% battery, LTE, moving, device hot (> 42 C)",dict(pct=70,charging=False,saver=False,net="LTE",motion="MOVING",hot=True)),
("7  35% battery, Wi-Fi, stationary",dict(pct=35,charging=False,saver=False,net="WIFI",motion="STATIONARY",hot=False))]
def always_on(net,seconds=3600):
    key="WIFI" if net=="WIFI" else "LTE"; n=seconds
    return dict(records=n,wakeups=n,energy_mAh=round((n*(E_SAMPLE+E_ENC)+n*E_UP_FIXED[key]+n*E_UP_REC[key])/3600,3))
def fleet(devices,records_each,interval=10,batch=300):
    """Scalability instrumentation: counts policy evaluations, radio wake-ups and queue size for a fleet."""
    evals=wake=0; maxq=0
    for d in range(devices):
        q=0; t=0; last=0
        for i in range(records_each):
            t+=interval; evals+=1; q+=1; maxq=max(maxq,q)
            if t-last>=batch: wake+=1; last=t; q=0
        if q: wake+=1
    return evals,wake,maxq
if __name__=="__main__":
    out={"scen":[],"validation":[],"scale":[],"energy_split":{}}
    for name,p in SCEN:
        r=simulate_hour(**p); r["name"]=name; r["baseline"]=always_on("WIFI" if p["net"]=="WIFI" else "LTE"); out["scen"].append(r)
        print(name,r["battery"],r["interval_s"],r["upload"],r["records"],r["sent"],r["wakeups"],r["energy_mAh"],r["useful_per_mAh"])
    # independent hand calculation (closed form written separately) for conditions 2, 3 and 6
    def hand(interval,period,key):
        n=3600/interval; w=3600/period
        return round((n*(60+0.05)+w*E_UP_FIXED[key]+n*E_UP_REC[key])/3600,3)
    out["validation"]=[dict(name="2  80% battery, LTE, moving",hand=hand(10,300,"LTE"),prog=out["scen"][1]["energy_mAh"],base=out["scen"][1]["baseline"]["energy_mAh"]),
                       dict(name="3  20% battery, LTE, stationary",hand=round((15*60.05+1*500+15*0.02)/3600,3),prog=out["scen"][2]["energy_mAh"],base=always_on("LTE")["energy_mAh"]),
                       dict(name="1  Charging on Wi-Fi, moving",hand=round((360*60.05+360*150+360*0.005)/3600,3),prog=out["scen"][0]["energy_mAh"],base=always_on("WIFI")["energy_mAh"])]
    tracemalloc.start()
    for n in (100,1000,10000):
        tracemalloc.reset_peak(); t0=time.time(); e,w,mq=fleet(1,n); cur,peak=tracemalloc.get_traced_memory()
        out["scale"].append(dict(kind="records",n=n,evals=e,wakeups=w,naive_wakeups=n,max_queue=mq,queue_kB=round(mq*(REC_BYTES+GCM_OVERHEAD)/1024,1),py_peak_kB=round(peak/1024,1)))
    for d in (1,5,10,20):
        e,w,mq=fleet(d,1000); out["scale"].append(dict(kind="devices",n=d,evals=e,wakeups=w,naive_wakeups=d*1000,max_queue=mq))
    # why batching does not make high-frequency tracking cheap: energy split for 1 h moving LTE
    for iv in (1,10,60):
        n=3600/iv; samp=n*(E_SAMPLE+E_ENC)/3600; up=(12*E_UP_FIXED["LTE"]+n*E_UP_REC["LTE"])/3600; nb=(n*E_UP_FIXED["LTE"]+n*E_UP_REC["LTE"])/3600
        out["energy_split"][str(iv)]=dict(sampling_mAh=round(samp,2),batched_upload_mAh=round(up,2),unbatched_upload_mAh=round(nb,2))
    json.dump(out,open("../res_tracker.json","w"),indent=1)
    for v in out["validation"]: print(v)
    for s in out["scale"]: print(s)
    print(out["energy_split"])
