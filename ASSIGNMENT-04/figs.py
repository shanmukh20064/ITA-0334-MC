import json,numpy as np,matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":8,"axes.spines.top":False,"axes.spines.right":False})
BL="#2F5496";OR="#C55A11";GR="#548235";GY="#7F7F7F";PU="#7030A0";NV="#1F3864"
def box(a,x,y,w,h,t,fc="#DEEAF6",ec=BL,fs=7.5,bold=False):
    a.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.02,rounding_size=0.08",fc=fc,ec=ec,lw=1.1)); a.text(x+w/2,y+h/2,t,ha="center",va="center",fontsize=fs,fontweight="bold" if bold else "normal")
def arr(a,p,q,c=GY,st="-|>",ls="-"): a.add_patch(FancyArrowPatch(p,q,arrowstyle=st,mutation_scale=9,lw=1.1,color=c,ls=ls))
def save(f,n): f.savefig(f"../img/{n}.png",dpi=200,bbox_inches="tight"); plt.close(f)
# ---- G1
f,a=plt.subplots(figsize=(7.4,5.0)); a.set_xlim(0,12); a.set_ylim(0,8.2); a.axis("off")
L=[("L7  Applications (one Linux UID per app)","Kotlin/Java code; calls SDK APIs","#E2EFDA",GR),
("L6  Application framework (system_server: Activity, Package, Power Mgrs)","Binder manager services; SECURITY: permission checks","#DEEAF6",BL),
("L5  Android Runtime ART (zygote-forked process; dex, JIT + profile AOT, GC)","RUNTIME here: managed execution, JNI to native","#FFF2CC","#BF9000"),
("L4  Native libraries (bionic, SQLite, BoringSSL, Skia) + HAL","C/C++ APIs and HAL interfaces (AIDL/HIDL)","#F2F2F2",GY),
("L3  Linux kernel (CFS, mm + LMK, Binder, SELinux, wakelocks, cpufreq)","KERNEL: syscalls, /dev; SECURITY: UID+SELinux; POWER: suspend","#FCE4D6",OR),
("L2  Device drivers (display, camera, radio, sensors, power)","ioctl and driver interfaces","#EDEDED",GY),
("L1  Hardware (SoC: big.LITTLE CPU, GPU, DSP; memory; radio; battery)","registers, interrupts","#D9D9D9",NV)]
for i,(t,e,fc,ec) in enumerate(L):
    y=7.1-i*1.1; box(a,0.1,y,7.0,0.85,t,fc,ec,6.0); box(a,7.3,y,4.6,0.85,e,"#FFFFFF",ec,5.8)
a.text(3.6,8.05,"Layer (name and responsibility)",ha="center",fontsize=7,fontweight="bold",color=NV); a.text(9.6,8.05,"What it exposes upward / where things sit",ha="center",fontsize=7,fontweight="bold",color=NV)
save(f,"i1_arch")
# ---- G2
f,a=plt.subplots(figsize=(7.4,3.2)); a.set_xlim(0,12); a.set_ylim(0,4.6); a.axis("off")
box(a,0.2,1.3,3.0,1.5,"ACTIVE\nscreen on or work running\nCPU awake, full DVFS","#E2EFDA",GR,6.6,True); box(a,4.5,1.3,3.0,1.5,"IDLE (light)\nscreen off, CPU brief awake\nnetwork ok, jobs batched","#FFF2CC","#BF9000",6.6,True); box(a,8.8,1.3,3.0,1.5,"SUSPENDED / DOZE\nCPU deep idle, radio off\npush + maintenance only","#FCE4D6",OR,6.6,True)
arr(a,(3.2,2.4),(4.5,2.4));a.text(3.85,2.7,"screen off,\nno wakelock",ha="center",fontsize=5.8);arr(a,(7.5,2.4),(8.8,2.4));a.text(8.15,2.7,"30 min still,\nunplugged",ha="center",fontsize=5.8)
arr(a,(8.8,1.7),(7.5,1.7));a.text(8.15,1.1,"push / window /\nmotion",ha="center",fontsize=5.8);arr(a,(4.5,1.7),(3.2,1.7));a.text(3.85,1.1,"unlock / alarm\n/ job due",ha="center",fontsize=5.8)
a.text(6,0.3,"From any state: power button or charger plugged in -> ACTIVE",ha="center",fontsize=6.3,color=GY)
save(f,"i2_power")
# ---- G3 RuralCare architecture (Part I Task 6)
f,a=plt.subplots(figsize=(7.2,4.6)); a.set_xlim(0,10); a.set_ylim(0,6.4); a.axis("off")
box(a,0.2,3.9,2.9,2.0,"CLASS A  Android\nKotlin app, ART\nRoom/SQLCipher DB\nKeystore key, WorkManager","#E2EFDA",GR,7,True); box(a,3.55,3.9,2.9,2.0,"CLASS B  iPhone\nSwift app, ARC\nCore Data + data protection\nKeychain, BGTaskScheduler","#DEEAF6",BL,7,True); box(a,6.9,3.9,2.9,2.0,"CLASS C  J2ME/JME or WML phone\nMIDlet (CLDC/MIDP)\nRMS record store (app-level AES)\nSMS / HTTP fallback","#FFF2CC","#BF9000",6.6,True)
box(a,1.5,1.9,7.0,1.0,"Sync gateway (HTTPS, TLS 1.2+; SMS-PIN gateway for Class C)\nidempotent API: device_id + record_uuid + sequence, ack by watermark","#FCE4D6",OR,7,True)
box(a,1.5,0.2,7.0,1.0,"RuralCare server: record store (dedup by record_uuid), key service (remote wipe/revoke), audit log","#D9D9D9",NV,7,True)
for x in (1.65,5.0,8.35): arr(a,(x,3.9),(x,2.9)); arr(a,(x,2.9),(x,3.9),"#999999","-")
arr(a,(5,1.9),(5,1.2)); arr(a,(5,1.2),(5,1.9),"#999999","-")
save(f,"i3_arch")
# ---- G4
f,a=plt.subplots(figsize=(7.4,4.4)); a.set_xlim(0,12); a.set_ylim(0,6.6); a.axis("off")
rows=[("UI layer\n(main thread)","Status screen, settings; ViewModel observes state only","#E2EFDA",GR),("Domain layer\n(background executor)","PolicyEngine: Policy[Battery][Network][Motion] -> {interval, upload}\nSamplingScheduler, SyncCoordinator","#DEEAF6",BL),
("Data layer\n(background executor)","EncryptingRecordQueue (AES-GCM, Keystore key) -> SQLite queue\nUploadClient (TLS, auth token)","#FFF2CC","#BF9000"),("OS services","Foreground service (location while moving) | WorkManager batch upload job\n(network + charging constraints) | BatteryManager, ConnectivityManager,\nActivityRecognition, thermal status | Android Keystore","#FCE4D6",OR)]
for i,(t,d,fc,ec) in enumerate(rows):
    y=5.1-i*1.65; box(a,0.1,y,3.0,1.25,t,fc,ec,6.8,True); box(a,3.3,y,8.6,1.25,d,"#FFFFFF",ec,6.4)
for i in range(3): arr(a,(1.6,5.1-i*1.65),(1.6,5.1-i*1.65-0.4),GY)
save(f,"p6_arch")
# ---- G5 Part II Task 2 results
b=json.load(open("../res_b2.json")); f,ax=plt.subplots(1,3,figsize=(7.4,2.8))
ax[0].bar(["single","2 threads","8 threads"],[b["blur1"]["mean_ms"],b["blur2"]["mean_ms"],b["blur8"]["mean_ms"]],color=[GY,BL,OR]); ax[0].set_ylabel("ms per run"); ax[0].set_title("(a) Image blur: normal case",fontsize=8)
ax[1].bar(["single","thread per task"],[b["tiny1"]["mean_ms"],b["tinyN"]["mean_ms"]],color=[GY,OR]); ax[1].set_ylabel("ms for 2000 tiny tasks"); ax[1].set_yscale("log"); ax[1].set_title("(b) Tiny tasks: counter-example",fontsize=8)
ax[2].bar(["1 thread","4 threads"],[b["cont1"]["mean_ms"],b["cont4"]["mean_ms"]],color=[GY,OR]); ax[2].set_ylabel("ms for 4M locked increments"); ax[2].set_title("(c) Lock contention",fontsize=8)
f.tight_layout(); save(f,"p2_res")
# ---- G6 Part II Task 3
r=json.load(open("../res_rt.json")); f,ax=plt.subplots(1,3,figsize=(7.4,2.8)); modes=[("interpret_only","interpret"),("c1_only","C1 JIT"),("tiered_default","tiered JIT")]
x=np.arange(3); ax[0].bar(x-.2,[r[m][w]["steady_ms"] for m,_ in modes for w in ["alloc"]],.4,color=BL,label="steady state"); ax[0].bar(x+.2,[r[m]["alloc"]["first_ms"] for m,_ in modes],.4,color=OR,label="first run (cold)"); ax[0].set_xticks(x); ax[0].set_xticklabels([n for _,n in modes]); ax[0].set_yscale("log"); ax[0].set_ylabel("ms"); ax[0].legend(frameon=False,fontsize=6); ax[0].set_title("(a) Allocation workload",fontsize=8)
ax[1].bar(x-.27,[r[m]["cpu"]["steady_ms"] for m,_ in modes],.27,color=BL,label="CPU"); ax[1].bar(x,[r[m]["alloc"]["steady_ms"] for m,_ in modes],.27,color=OR,label="alloc"); ax[1].bar(x+.27,[r[m]["list"]["steady_ms"] for m,_ in modes],.27,color=GR,label="list"); ax[1].set_xticks(x); ax[1].set_xticklabels([n for _,n in modes]); ax[1].set_yscale("log"); ax[1].set_ylabel("steady-state ms"); ax[1].legend(frameon=False,fontsize=6); ax[1].set_title("(b) Three workloads",fontsize=8)
ax[2].bar(x,[r[m]["total_ms"] for m,_ in modes],color=[GY,BL,OR]); ax[2].set_xticks(x); ax[2].set_xticklabels([n for _,n in modes]); ax[2].set_yscale("log"); ax[2].set_ylabel("total benchmark ms"); ax[2].set_title("(c) Whole run",fontsize=8)
f.tight_layout(); save(f,"p3_res")
# ---- G7 Part II Task 5
p=json.load(open("../res_power.json")); f,ax=plt.subplots(1,2,figsize=(7.4,3.0))
lab=["big 1.0G","big 2.0G","big 2.8G"]; d=[x for x in p["dvfs"]]
ax[0].bar([f"{x['core'][0].upper()}{x['f']}" for x in d],[x["E_J"] for x in d],color=[BL]*4+[OR]*3); ax[0].set_ylabel("energy per task in a 10 s window (J)"); ax[0].set_title("(a) DVFS: energy per task (L = little, B = big, MHz)",fontsize=7.2); ax[0].tick_params(axis="x",labelsize=6.5)
c=p["configs"]; ax[1].barh(["A wakelock","B alarms","C Doze","D batching","E conflict 1","F conflict 2"][::-1],[x["total_mAh"] for x in c][::-1],color=[GY,GY,GR,GR,OR,OR][::-1]); ax[1].set_xlabel("mAh over 8 h"); ax[1].set_title("(b) OS idle control and batching",fontsize=8)
f.tight_layout(); save(f,"p5_res")
# ---- G8 Part II Task 6
t=json.load(open("../res_tracker.json")); f,ax=plt.subplots(1,2,figsize=(7.4,3.0))
nm=[s["name"].split()[0] for s in t["scen"]]; ax[0].bar(nm,[s["energy_mAh"] for s in t["scen"]],color=BL); ax[0].set_xlabel("operating condition"); ax[0].set_ylabel("energy per hour (mAh)"); ax[0].set_title("(a) Energy by condition",fontsize=8)
iv=["1","10","60"]; xx=np.arange(3); ax[1].bar(xx-.27,[t["energy_split"][i]["sampling_mAh"] for i in iv],.27,color=BL,label="sampling"); ax[1].bar(xx,[t["energy_split"][i]["batched_upload_mAh"] for i in iv],.27,color=GR,label="batched upload"); ax[1].bar(xx+.27,[t["energy_split"][i]["unbatched_upload_mAh"] for i in iv],.27,color=OR,label="unbatched upload"); ax[1].set_yscale("log"); ax[1].set_xticks(xx); ax[1].set_xticklabels(["1 s","10 s","60 s"]); ax[1].set_xlabel("sampling interval"); ax[1].set_ylabel("mAh per hour"); ax[1].legend(frameon=False,fontsize=6); ax[1].set_title("(b) Where the energy goes (LTE)",fontsize=8)
f.tight_layout(); save(f,"p6_res")
print("ok")
