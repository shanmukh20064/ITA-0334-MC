import subprocess,resource,json,os,statistics as st
env=dict(os.environ); env.pop("JAVA_TOOL_OPTIONS",None)
def run(sc,reps):
    r0=resource.getrusage(resource.RUSAGE_CHILDREN)
    o=subprocess.run(["java","-Xmx512m","Bench2",sc,str(reps)],capture_output=True,text=True,env=env).stdout.strip().splitlines()[-1]
    r1=resource.getrusage(resource.RUSAGE_CHILDREN)
    d=dict(x.split("=") for x in o.split("|")[1:]); d={k:float(v) for k,v in d.items()}
    d["vol"]=r1.ru_nvcsw-r0.ru_nvcsw; d["invol"]=r1.ru_nivcsw-r0.ru_nivcsw; d["maxrss_mb"]=r1.ru_maxrss/1024
    return d
base=[run("none",0) if False else None]
res={}
for sc,reps in [("blur1",15),("blur2",15),("blur8",15),("tiny1",15),("tinyN",15),("cont1",15),("cont4",15)]:
    runs=[run(sc,reps) for _ in range(3)]
    res[sc]={k:st.median(r[k] for r in runs) for k in runs[0]}
    res[sc]["reps"]=reps
json.dump(res,open("../res_b2.json","w"),indent=1)
for k,v in res.items(): print(k,{a:round(b,1) for a,b in v.items()})
