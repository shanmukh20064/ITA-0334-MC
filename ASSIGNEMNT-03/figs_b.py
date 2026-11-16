import json, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":8,"axes.spines.top":False,"axes.spines.right":False})
BL="#2F5496";OR="#C55A11";GR="#548235";GY="#7F7F7F";PU="#7030A0"
L=lambda n:json.load(open(f"../{n}.json"))
def save(f,n): f.tight_layout(); f.savefig(f"../img/{n}.png",dpi=200); plt.close(f)
# Q1
q=L("res_q1"); f,ax=plt.subplots(2,2,figsize=(7.4,5.0))
a=ax[0,0]; a.plot([r["v"] for r in q["speed"]],[r["down"] for r in q["speed"]],"o-",color=OR); a.set_xlabel("speed (m/s)"); a.set_ylabel("seconds without service per trip"); a.set_title("(a) Outage per trip vs speed",fontsize=8)
a=ax[0,1]; x=np.arange(4); a.bar(x-.2,[r["handoffs"] for r in q["hys"]],.4,color=BL,label="handoffs"); a.bar(x+.2,[r["pingpong"] for r in q["hys"]],.4,color=OR,label="ping-pong"); a.set_xticks(x); a.set_xticklabels([f"{r['H']} dB" for r in q["hys"]]); a.set_xlabel("hysteresis margin"); a.legend(frameon=False); a.set_title("(b) Handoffs per trip vs hysteresis",fontsize=8)
a=ax[1,0]; a.plot([r["S"] for r in q["spacing"]],[100*r["pdr"] for r in q["spacing"]],"o-",color=GR); a.set_xlabel("AP spacing (m), range about 250 m"); a.set_ylabel("on-time delivery (%)"); a.set_title("(c) Coverage overlap vs delivery",fontsize=8)
a=ax[1,1]; a.plot([r["others"] for r in q["load"]],[r["delay"] for r in q["load"]],"o-",color=PU); a.set_yscale("log"); a.set_xlabel("other users on the same AP"); a.set_ylabel("mean delay (ms)"); a.set_title("(d) Load vs delay",fontsize=8)
save(f,"r1")
# Q2
q=L("res_q2"); f,ax=plt.subplots(1,2,figsize=(7.4,3.0))
for v,c,n in (("basic",OR,"basic"),("trigger",BL,"link-layer trigger"),("smooth",GR,"smooth handoff"),("ro",PU,"route optimisation")):
    r=[x for x in q["dwell"] if x["variant"]==v]; ax[0].plot([x["T"] for x in r],[x["loss_pct"] for x in r],"o-",color=c,label=n)
ax[0].set_xscale("log"); ax[0].set_yscale("log"); ax[0].invert_xaxis(); ax[0].set_xlabel("time between handoffs (s)"); ax[0].set_ylabel("packets lost (%)"); ax[0].legend(frameon=False,fontsize=6.5); ax[0].set_title("(a) Loss vs mobility",fontsize=8)
pl=[20,160,512,1400]; ax[1].bar([str(p) for p in pl],[q["overhead"][str(p)]["pct"] for p in pl],color=BL); ax[1].set_xlabel("payload bytes"); ax[1].set_ylabel("IP-in-IP overhead (%)"); ax[1].set_title("(b) Tunnel overhead per packet",fontsize=8)
save(f,"r2")
# Q3
q=L("res_q3"); f,ax=plt.subplots(1,3,figsize=(7.4,2.8))
a=ax[0]; a.plot([100*r["f"] for r in q["cross"]],[100*r["cellular"] for r in q["cross"]],"o-",color=BL,label="cellular (9 BS)"); a.plot([100*r["f"] for r in q["cross"]],[100*r["adhoc_half"] for r in q["cross"]],"s-",color=OR,label="ad hoc, nodes fail at half rate"); a.plot([100*r["f"] for r in q["cross"]],[100*r["adhoc_same"] for r in q["cross"]],"^--",color=GY,label="ad hoc, same failure rate")
a.set_xlabel("infrastructure failed (%)"); a.set_ylabel("user pairs that can talk (%)"); a.legend(frameon=False,fontsize=5.8); a.set_title("(a) Survival, 150 users",fontsize=8)
a=ax[1]; a.plot([r["N"] for r in q["density"]],[100*r["conn"] for r in q["density"]],"o-",color=OR); a.set_xlabel("ad hoc nodes in 2 km x 2 km"); a.set_ylabel("pairs connected (%)"); a.set_title("(b) Density needed",fontsize=8)
a=ax[2]; a.plot([r["n"] for r in q["scale"]],[r["cellular"] for r in q["scale"]],"o-",color=BL,label="cellular"); a.plot([r["n"] for r in q["scale"]],[r["adhoc"] for r in q["scale"]],"s-",color=OR,label="ad hoc"); a.set_xscale("log"); a.set_yscale("log"); a.set_xlabel("users"); a.set_ylabel("per-user Mbps (model)"); a.legend(frameon=False,fontsize=6.5); a.set_title("(c) Capacity per user",fontsize=8)
save(f,"r3")
# Q4
q=L("res_q4"); f,ax=plt.subplots(1,2,figsize=(7.4,2.9)); n=["Basic","+ trigger","+ smooth","+ smooth\n+ backup"]; x=np.arange(len(n))
ax[0].bar(x-.2,[c["handoff_out"] for c in q["cfg"]],.4,color=BL,label="handoff outage"); ax[0].bar(x+.2,[c["dead_out"] for c in q["cfg"]],.4,color=OR,label="coverage-hole outage"); ax[0].set_xticks(x); ax[0].set_xticklabels(n,fontsize=6.5); ax[0].set_ylabel("seconds per 24 km trip"); ax[0].legend(frameon=False,fontsize=6.5,loc="upper center",bbox_to_anchor=(0.5,0.9)); ax[0].set_ylim(0,58); ax[0].set_title("(a) Interruption per trip",fontsize=8)
ax[1].bar(x,[c["loss_v"] for c in q["cfg"]],color=GR); ax[1].set_xticks(x); ax[1].set_xticklabels(n,fontsize=6.5); ax[1].set_ylabel("vitals packets lost (%)"); ax[1].set_title("(b) Vitals lost",fontsize=8)
save(f,"r4")
# Q5
m=L("res_manet"); dd=L("res_dsdv"); f,ax=plt.subplots(1,3,figsize=(7.4,2.8))
Ns=[10,20,40,80]; ax[0].plot(Ns,[m["size"][f"DSDV_{N}"]["ctl_pk"] for N in Ns],"o-",color=BL,label="DSDV"); ax[0].plot(Ns,[m["size"][f"AODV_{N}"]["ctl_pk"] for N in Ns],"s-",color=OR,label="AODV"); ax[0].set_xlabel("nodes"); ax[0].set_ylabel("control packets / s"); ax[0].legend(frameon=False); ax[0].set_title("(a) Overhead vs size",fontsize=8)
sp=[0,1,2,5,10,20]; ax[1].plot(sp,[100*m["speed"][f"DSDV_{v}"]["pdr"] for v in sp],"o-",color=BL); ax[1].plot(sp,[100*m["speed"][f"AODV_{v}"]["pdr"] for v in sp],"s-",color=OR); ax[1].set_xlabel("mean speed (m/s)"); ax[1].set_ylabel("delivery ratio (%)"); ax[1].set_title("(b) Delivery vs mobility",fontsize=8)
Ps=[2,5,15,30]; ax[2].plot([m["sens"][f"DSDV_P{p}"]["ctl_pk"] for p in Ps],[100*m["sens"][f"DSDV_P{p}"]["pdr"] for p in Ps],"o-",color=BL)
for p in Ps: ax[2].annotate(f"{p} s",(m["sens"][f"DSDV_P{p}"]["ctl_pk"],100*m["sens"][f"DSDV_P{p}"]["pdr"]),fontsize=6.5,xytext=(3,3),textcoords="offset points")
ax[2].set_xlabel("control packets / s"); ax[2].set_ylabel("delivery (%)"); ax[2].set_title("(c) DSDV update interval",fontsize=8)
save(f,"r5")
# Q6
f,ax=plt.subplots(1,3,figsize=(7.4,2.8)); sz=["size"]; 
x=np.arange(4); ax[0].bar(x-.2,[100*m["size"][f"DSDV_{N}"]["pdr"] for N in Ns],.4,color=BL,label="DSDV"); ax[0].bar(x+.2,[100*m["size"][f"AODV_{N}"]["pdr"] for N in Ns],.4,color=OR,label="AODV"); ax[0].set_xticks(x); ax[0].set_xticklabels(Ns); ax[0].set_xlabel("nodes"); ax[0].set_ylabel("delivery (%)"); ax[0].legend(frameon=False,fontsize=6.5); ax[0].set_title("(a) Delivery",fontsize=8)
ax[1].bar(x-.2,[m["size"][f"DSDV_{N}"]["nrl"] for N in Ns],.4,color=BL); ax[1].bar(x+.2,[m["size"][f"AODV_{N}"]["nrl"] for N in Ns],.4,color=OR); ax[1].set_yscale("log"); ax[1].set_xticks(x); ax[1].set_xticklabels(Ns); ax[1].set_xlabel("nodes"); ax[1].set_ylabel("control packets per data packet"); ax[1].set_title("(b) Normalised routing load",fontsize=8)
ax[2].bar(["DSDV","AODV"],[1000*m["size"]["DSDV_40"]["first"],1000*m["size"]["AODV_40"]["first"]],color=[BL,OR]); ax[2].set_ylabel("first-packet delay (ms)"); ax[2].set_title("(c) Initial delay, 40 nodes",fontsize=8)
save(f,"r6")
# Q7
q=L("res_q7"); qx=L("res_q7x"); f,ax=plt.subplots(2,2,figsize=(7.4,5.0))
a=ax[0,0]; a.plot(Ns,[100*q["size"][f"DSDV_{N}"]["pdr"] for N in Ns],"o-",color=BL,label="DSDV (15 s)"); a.plot(Ns,[100*q["size"][f"AODV_{N}"]["pdr"] for N in Ns],"s-",color=OR,label="AODV"); a.set_xlabel("mobile nodes"); a.set_ylabel("delivery (%)"); a.legend(frameon=False,fontsize=6.5); a.set_title("(a) Number of nodes",fontsize=8)
sp=[2,10,20,30]; a=ax[0,1]; a.plot(sp,[100*q["speed"][f"DSDV_{v}"]["pdr"] for v in sp],"o-",color=BL); a.plot(sp,[100*q["speed"][f"AODV_{v}"]["pdr"] for v in sp],"s-",color=OR); a.set_xlabel("mean speed (m/s)"); a.set_ylabel("delivery (%)"); a.set_title("(b) Mobility (40 nodes)",fontsize=8)
a=ax[1,0]; names=["DSDV","AODV","AODV+buffer"]; x=np.arange(3); a.bar(x-.2,[100*q["fail"][k]["pdr_before"] for k in names],.4,color=GY,label="before failure"); a.bar(x+.2,[100*q["fail"][k]["pdr_after"] for k in names],.4,color=OR,label="after 30% nodes fail"); a.set_xticks(x); a.set_xticklabels(names); a.set_ylabel("delivery (%)"); a.legend(frameon=False,fontsize=6.5); a.set_title("(c) Node failure",fontsize=8)
a=ax[1,1]; names=["DSDV","AODV","AODV+buffer"]; a.bar(x,[100*q["discon"][k]["pdr"] for k in names],color=[BL,OR,GR]); a.set_xticks(x); a.set_xticklabels(names); a.set_ylabel("delivery (%)"); a.set_title("(d) Partitioned network (12 nodes)",fontsize=8)
save(f,"r7")
print("ok")
