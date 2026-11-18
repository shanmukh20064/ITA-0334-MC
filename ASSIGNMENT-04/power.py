"""Task 5 (Part II): documented power model (assumed constants, typical of a mid-range phone). Not a measurement of a real device."""
import json
BAT=4000.0         # mAh
I_SUSP=4.0         # mA, suspended (screen off, CPU in deep idle)
I_AWAKE=60.0       # mA, CPU awake but idle (held partial wakelock)
I_WAKE_TRANS=120.0; T_WAKE_TRANS=0.4      # resume transition
I_RADIO=180.0; I_TAIL=100.0; T_TAIL=5.0   # LTE active and tail
# --- Technique 1: DVFS. P = Pstatic + k*f*V^2 ; task of W cycles
CORES={"little":dict(ps=0.03,levels=[(500,0.60),(1000,0.70),(1500,0.85),(1800,0.95)],pmax=0.35),
       "big":dict(ps=0.15,levels=[(1000,0.70),(2000,0.90),(2800,1.10)],pmax=1.30)}
def dvfs(W=400e6,window=10.0,p_idle=I_SUSP*3.85/1000):
    rows=[]
    for name,c in CORES.items():
        fmax,vmax=c["levels"][-1]; k=(c["pmax"]-c["ps"])/(fmax*1e6*vmax**2)
        for f,v in c["levels"]:
            P=c["ps"]+k*f*1e6*v*v; t=W/(f*1e6); E=P*t+p_idle*max(0,window-t)
            rows.append(dict(core=name,f=f,V=v,P_W=round(P,3),t_s=round(t,3),E_J=round(E,3),meets_2s=t<=2.0))
    return rows
# --- Techniques 2 and 3: idle control and batching over 8 h, screen off, app wants a sync every 60 s
H=8*3600
def wake_cost(radio_s=2.0): return (I_WAKE_TRANS*T_WAKE_TRANS+150*2.0+I_RADIO*radio_s+I_TAIL*T_TAIL)/3600.0   # mAh per wake-up
def config(name,wakeups,radio_s,awake_always=False):
    base=(I_AWAKE if awake_always else I_SUSP)*H/3600.0
    sync=wakeups*wake_cost(radio_s)
    return dict(name=name,wakeups=wakeups,baseline_mAh=round(base,1),wake_mAh=round(sync,1),total_mAh=round(base+sync,1),pct_battery=round(100*(base+sync)/BAT,1))
doze_windows=[1800]; gap=1800
for g in [1800,3600,7200,7200,7200,7200]:
    doze_windows.append(doze_windows[-1]+g)
doze_windows=[w for w in doze_windows if w<=H]
def run_all():
    r=[]
    r.append(config("A  Baseline: partial wakelock held, sync every 60 s",480,2.0,True))
    r.append(config("B  No wakelock, alarm every 60 s (device moving, so no Doze)",480,2.0))
    r.append(config("C  Doze (stationary): sync only in maintenance windows",len(doze_windows),2.0+(3600/60)*0.05))
    r.append(config("D  Batching: one JobScheduler batch every 5 min, no Doze",96,2.0+5*0.2))
    r.append(config("E  Conflict 1: Doze-eligible device, but a foreground service keeps a wakelock (app exempt from Doze)",480,2.0,True))
    r.append(config("F  Conflict 2: Doze on, but the app uses exact alarms (setExactAndAllowWhileIdle, about 1 per 9 min)",int(H/540),2.0))
    return r
def trace(hours=2):
    ev=[]
    ev.append((0,"screen off, device stationary -> idle timer starts (light idle)"))
    ev.append((1800,"Doze (deep idle) entered: network access and alarms deferred; wake locks ignored"))
    ev.append((1800,"maintenance window #1 (about 1 min): job runs, batch upload, radio on"))
    ev.append((3600,"window #2 after 30 min gap"))
    ev.append((7200,"window #3 after 60 min gap"))
    return [e for e in ev if e[0]<=hours*3600]
if __name__=="__main__":
    out=dict(dvfs=dvfs(),configs=run_all(),windows=doze_windows,wake_cost_mAh=round(wake_cost(),3),trace=trace())
    json.dump(out,open("../res_power.json","w"),indent=1)
    for r in out["dvfs"]: print(r)
    for r in out["configs"]: print(r)
    print(doze_windows)
