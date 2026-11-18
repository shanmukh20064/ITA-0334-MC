"""Part II Task 1: model of the Android process-importance / low-memory-kill policy (documented oom_adj classes). A MODEL, not an emulator log."""
import json
ADJ={"foreground":0,"visible":100,"perceptible":200,"service":500,"home":600,"previous":700,"cached":900}
# documented-style minfree table: when free memory falls below X MB, processes with adj >= A may be killed
MINFREE=[(150,900),(100,700),(70,500),(40,200),(25,100),(15,0)]
def procs(testapp_state):
    base=[("system_server","foreground",300),("com.android.launcher","home",120),("com.android.systemui","perceptible",180),("chat.app","cached",40),("maps.app","cached",60),("mail.app","previous",50)]
    state={"foreground":"foreground","background5":"cached","lowmem":"cached"}[testapp_state]
    return base+[("com.example.testapp",state,85)]
def kill_order(plist,free_mb):
    killed=[]
    for pname,cls,rss in sorted(plist,key=lambda p:(-ADJ[p[1]],-p[2])):
        thr=[a for (mb,a) in MINFREE if free_mb<mb]
        if thr and ADJ[cls]>=min(thr) and ADJ[cls]>0: killed.append(pname); free_mb+=rss
    return killed
def run(case,free):
    pl=procs(case); k=kill_order(pl,free); app=[p for p in pl if p[0]=="com.example.testapp"][0]
    alive="killed" if app[0] in k else "alive"
    return dict(case=case,free_mb=free,test_adj=ADJ[app[1]],test_class=app[1],killed=k,test_app=alive)
res=[run("foreground",200),run("background5",160),run("lowmem",120),run("lowmem",20)]
json.dump(res,open("../res_lmk.json","w"),indent=1)
for r in res: print(r)
