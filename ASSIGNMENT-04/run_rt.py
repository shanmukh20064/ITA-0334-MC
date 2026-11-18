import subprocess,os,json,re,statistics as st
env=dict(os.environ);env.pop("JAVA_TOOL_OPTIONS",None)
def j(args,mode): return subprocess.run(["java","-XX:+UseSerialGC","-Xmx64m"]+args+["RuntimeBench",mode],capture_output=True,text=True,env=env).stdout
res={}
for name,args in [("interpret_only",["-Xint"]),("c1_only",["-XX:TieredStopAtLevel=1"]),("tiered_default",[])]:
    runs=[]
    for _ in range(3):
        o=j(args,"bench"); d={}
        for l in o.splitlines():
            p=l.split("|")
            if p[0]=="WL": d[p[1]]={k:float(v) for k,v in (x.split("=") for x in p[2:])}
            if p[0]=="TOTAL": d["total_ms"]=float(p[1].split("=")[1])
            if p[0]=="GC": d["gc"]={k:float(v) for k,v in (x.split("=") for x in p[2:])}
        runs.append(d)
    m={}
    for w in ["cpu","alloc","list"]:
        m[w]={k:st.median(r[w][k] for r in runs) for k in runs[0][w]}
    m["total_ms"]=st.median(r["total_ms"] for r in runs); m["gc"]={k:st.median(r["gc"][k] for r in runs) for k in runs[0]["gc"]}
    res[name]=m
res["leak"]=j([],"leak").strip(); res["block"]=j([],"block").strip()
json.dump(res,open("../res_rt.json","w"),indent=1)
print(json.dumps(res,indent=1))
