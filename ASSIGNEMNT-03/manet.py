"""Seeded MANET simulator: random-waypoint mobility, DSDV (proactive) and AODV (reactive).
Time step 1 s.  Assumptions (stated in the report): per-hop delay 10 ms, radio range 250 m (unit-disk),
no MAC collisions, link-layer feedback detects a broken link, flooding costs one transmission per node that rebroadcasts."""
import numpy as np, math
INF=10**6
HD=0.010          # per-hop forwarding delay (s)  [assumption]
IPUDP=28          # IP+UDP header bytes
def rwp(N,area,v,T,rng,pause=2.0):
    """random waypoint, speed uniform(0.5v,1.5v); returns pos[T+1,N,2] sampled every second"""
    pos=np.zeros((T+1,N,2)); p=rng.uniform(0,area,(N,2)); tgt=rng.uniform(0,area,(N,2))
    sp=rng.uniform(0.5*v,1.5*v,N) if v>0 else np.zeros(N); wait=np.zeros(N)
    for t in range(T+1):
        pos[t]=p
        for _ in range(1):
            for i in range(N):
                if v==0: continue
                if wait[i]>0: wait[i]=max(0,wait[i]-1); continue
                d=tgt[i]-p[i]; L=np.hypot(*d)
                if L<=sp[i]: p[i]=tgt[i]; tgt[i]=rng.uniform(0,area,2); sp[i]=rng.uniform(0.5*v,1.5*v); wait[i]=pause
                else: p[i]=p[i]+d/L*sp[i]
    return pos
def adjacency(pos,R):
    d=np.linalg.norm(pos[:,None,:]-pos[None,:,:],axis=2); A=(d<=R); np.fill_diagonal(A,False); return A
def bfs(A,s,maxd=10**9):
    N=len(A); dist=np.full(N,-1); par=np.full(N,-1); dist[s]=0; fr=[s]
    while fr:
        nf=[]
        for u in fr:
            if dist[u]>=maxd: continue
            for w in np.nonzero(A[u])[0]:
                if dist[w]<0: dist[w]=dist[u]+1; par[w]=u; nf.append(w)
        fr=nf
    return dist,par
class Ctl:
    def __init__(s): s.pk={}; s.by={}
    def add(s,kind,n,size):
        s.pk[kind]=s.pk.get(kind,0)+n; s.by[kind]=s.by.get(kind,0)+n*size
    def tot(s): return sum(s.pk.values())
    def totb(s): return sum(s.by.values())
# ------------------------------------------------------------------ DSDV
class DSDV:
    def __init__(s,N,rng,P=15.0):
        s.N=N; s.P=P; s.seq=np.zeros((N,N),int); s.met=np.full((N,N),INF); s.nh=np.full((N,N),-1)
        for i in range(N): s.met[i,i]=0; s.nh[i,i]=i
        s.phase=rng.uniform(0,P,N); s.changed=np.zeros((N,N),bool); s.ctl=Ctl(); s.last=None
    def _recv(s,r,u,dests,mets,seqs):
        """r receives from neighbour u a list of entries"""
        for d,m,sq in zip(dests,mets,seqs):
            if d==r: continue
            m2=INF if m>=INF else m+1
            if sq>s.seq[r,d] or (sq==s.seq[r,d] and m2<s.met[r,d]):
                s.seq[r,d]=sq; s.met[r,d]=m2; s.nh[r,d]=u if m2<INF else -1; s.changed[r,d]=True
    def _bcast(s,u,A,full):
        N=s.N
        if full: ds=np.arange(N); s.seq[u,u]+=2; s.met[u,u]=0
        else: ds=np.nonzero(s.changed[u])[0]
        if len(ds)==0: return
        s.changed[u,:]=False
        s.ctl.add("update",1,IPUDP+12*len(ds))
        for r in np.nonzero(A[u])[0]: s._recv(r,u,ds,s.met[u,ds],s.seq[u,ds])
    def step(s,t,A):
        N=s.N
        if s.last is not None:                     # link-layer detection of lost neighbours
            lost=s.last&~A
            for r,u in zip(*np.nonzero(lost)):
                mk=(s.nh[r]==u)&(s.met[r]<INF)
                if mk.any():
                    s.met[r,mk]=INF; s.nh[r,mk]=-1; s.seq[r,mk]+=1; s.changed[r,mk]=True
        s.last=A.copy()
        for i in range(N):                          # periodic full dumps
            if int(t+s.phase[i])//int(s.P)!=int(t-1+s.phase[i])//int(s.P): s._bcast(i,A,True)
        rounds=0
        while s.changed.any() and rounds<40:        # triggered incremental updates, one broadcast per node per round
            for u in np.nonzero(s.changed.any(axis=1))[0]: s._bcast(u,A,False)
            rounds+=1
        return rounds
    def path(s,A,src,dst):
        cur=src; hops=0
        while cur!=dst:
            if s.met[cur,dst]>=INF: return None
            n=s.nh[cur,dst]
            if n<0 or not A[cur,n]: return None
            cur=n; hops+=1
            if hops>s.N: return None
        return hops
# ------------------------------------------------------------------ AODV
class AODV:
    def __init__(s,N,rng,active_to=3.0,hello=False,local_repair=False):
        s.N=N; s.to=active_to; s.hello=hello; s.lr=local_repair
        s.nh=np.full((N,N),-1); s.hops=np.zeros((N,N),int); s.exp=np.full((N,N),-1.0)
        s.ctl=Ctl(); s.buf={}; s.fail_until={}; s.disc_lat=[]; s.disc_n=0; s.disc_fail=0; s.reps=0
    def valid(s,t,r,d): return s.exp[r,d]>t and s.nh[r,d]>=0
    def path_ok(s,t,A,src,dst):
        cur=src;h=0
        while cur!=dst:
            if not s.valid(t,cur,dst): return None
            n=s.nh[cur,dst]
            if not A[cur,n]: return None
            cur=n;h+=1
            if h>s.N: return None
        return h
    def discover(s,t,A,src,dst,ttl_first=3):
        """expanding-ring RREQ flooding; returns latency or None. Costs counted as transmissions."""
        s.disc_n+=1; lat=0.0
        for ttl,tmo in ((ttl_first,0.4),(s.N,2.8),(s.N,2.8)):
            dist,par=bfs(A,src,ttl)
            tx=1+sum(1 for w in range(s.N) if dist[w]>=1 and dist[w]<ttl and w!=dst)
            s.ctl.add("RREQ",tx,IPUDP+24)
            if dist[dst]>=1:
                h=int(dist[dst]); s.ctl.add("RREP",h,IPUDP+20)
                # install forward routes along tree path and reverse routes
                cur=dst; 
                while par[cur]>=0:
                    p=par[cur]; s.nh[p,dst]=cur; s.hops[p,dst]=dist[dst]-dist[p]; s.exp[p,dst]=t+s.to
                    s.nh[cur,src]=p; s.hops[cur,src]=dist[cur]; s.exp[cur,src]=t+s.to
                    cur=p
                lat+=2*h*(HD+0.005)
                s.disc_lat.append(lat); return lat
            lat+=tmo
            if ttl>=s.N and tmo==2.8 and s.reps==0: pass
        s.disc_fail+=1; return None
    def hello_cost(s):
        if s.hello: s.ctl.add("HELLO",s.N,IPUDP+20)
    def send(s,t,A,src,dst):
        """returns (delivered, delay)"""
        delay=0.0; cur=src; hops=0
        if not s.valid(t,src,dst) or s.path_ok(t,A,src,dst) is None:
            key=(src,dst)
            if t<s.fail_until.get(key,-1): return False,0.0
            # if the route simply broke, invalidate and rediscover
            lat=s.discover(t,A,src,dst)
            if lat is None: s.fail_until[key]=t+5.0; return False,0.0
            delay+=lat
        while cur!=dst:
            n=s.nh[cur,dst]
            if n<0 or not s.valid(t,cur,dst): return False,delay
            if not A[cur,n]:
                # link break discovered while forwarding
                if s.lr and s.hops[cur,dst]>0:
                    dist,par=bfs(A,cur,min(s.N,int(s.hops[cur,dst])+2))
                    tx=1+sum(1 for w in range(s.N) if 1<=dist[w]<int(s.hops[cur,dst])+2 and w!=dst)
                    s.ctl.add("RREQ",tx,IPUDP+24)
                    if dist[dst]>=1:
                        s.ctl.add("RREP",int(dist[dst]),IPUDP+20); c=dst
                        while par[c]>=0:
                            p=par[c]; s.nh[p,dst]=c; s.hops[p,dst]=dist[dst]-dist[p]; s.exp[p,dst]=t+s.to; c=p
                        delay+=2*dist[dst]*(HD+0.005); continue
                # RERR back to the source along the reverse route
                up=0;x=cur
                while x!=src and s.nh[x,src]>=0 and up<s.N: x=s.nh[x,src]; up+=1
                s.ctl.add("RERR",max(1,up),IPUDP+12)
                s.exp[cur,dst]=-1; s.exp[src,dst]=-1
                return False,delay
            s.exp[cur,dst]=t+s.to; s.exp[cur,src]=max(s.exp[cur,src],t+s.to)
            cur=n; hops+=1; delay+=HD
            if hops>s.N: return False,delay
        return True,delay
def simulate(proto,N,v,T=200,area=1000.0,R=250.0,nflows=8,rate=2,warm=30,seed=1,opts=None,fail_frac=0.0,fail_at=100,pos=None,flows=None):
    opts=opts or {}
    rng=np.random.default_rng(seed)
    if pos is None: pos=rwp(N,area,v,T,rng)
    if flows is None:
        flows=[]
        while len(flows)<nflows:
            a,b=rng.choice(N,2,replace=False); flows.append((int(a),int(b)))
    P=DSDV(N,np.random.default_rng(seed+1000),P=opts.get("P",15.0)) if proto=="DSDV" else AODV(N,np.random.default_rng(seed+1000),opts.get("active_to",3.0),opts.get("hello",False),opts.get("lr",False))
    dead=np.zeros(N,bool)
    if fail_frac>0:
        cand=[i for i in range(N) if i not in {x for f in flows for x in f}]
        k=int(round(fail_frac*N)); dead[rng.choice(cand,min(k,len(cand)),replace=False)]=True
    st={};dv={}
    sent=0;deliv=0;delays=[];first=[];seen=set();avail=0;samples=0;late=0
    bufs={f:[] for f in flows}; nexttry={f:0 for f in flows}; bufmax=opts.get("buffer",0)
    for t in range(T+1):
        A=adjacency(pos[t],R)
        if fail_frac>0 and t>=fail_at: A=A.copy(); A[dead,:]=False; A[:,dead]=False
        if proto=="DSDV": P.step(t,A)
        else: P.hello_cost() if t>0 else None
        if t>=warm and bufmax>0 and proto=="AODV":
            for f in flows:                       # store-carry-forward: retry buffered packets every 5 s
                b=bufs[f]
                b[:]=[x for x in b if t-x<=bufmax]
                if b and t>=nexttry[f]:
                    nexttry[f]=t+5; P.fail_until.pop(f,None)
                    okd,dl=P.send(t,A,f[0],f[1])
                    if okd:
                        for x in b: deliv+=1; dv[t]=dv.get(t,0)+1; delays.append(dl+(t-x))
                        b.clear()
        if t>=warm:
            for (s_,d_) in flows:
                samples+=1
                ok=(P.path(A,s_,d_) is not None) if proto=="DSDV" else (P.path_ok(t,A,s_,d_) is not None)
                avail+=1 if ok else 0
                for k in range(rate):
                    sent+=1; st[t]=st.get(t,0)+1
                    if proto=="DSDV":
                        h=P.path(A,s_,d_)
                        if h is None: continue
                        deliv+=1; dv[t]=dv.get(t,0)+1; dl=h*HD
                    else:
                        okd,dl=P.send(t,A,s_,d_)
                        if not okd:
                            if bufmax>0: bufs[(s_,d_)].append(t)
                            continue
                        deliv+=1; dv[t]=dv.get(t,0)+1
                    delays.append(dl)
                    if (s_,d_) not in seen: seen.add((s_,d_)); first.append(dl)
    dur=T-warm+1
    sa=sum(v for k,v in st.items() if k>=fail_at); da=sum(v for k,v in dv.items() if k>=fail_at); sb=sum(v for k,v in st.items() if k<fail_at); db=sum(v for k,v in dv.items() if k<fail_at)
    out=dict(pdr_after=da/max(1,sa),pdr_before=db/max(1,sb),pdr=deliv/max(1,sent),delay=float(np.mean(delays)) if delays else float("nan"),
             delay95=float(np.percentile(delays,95)) if delays else float("nan"),
             first=float(np.mean(first)) if first else float("nan"),avail=avail/max(1,samples),
             ctl_pk=P.ctl.tot()/T,ctl_by=P.ctl.totb()/T,nrl=P.ctl.tot()/max(1,deliv),sent=sent,deliv=deliv,
             kinds={k:v/T for k,v in P.ctl.pk.items()})
    if proto=="AODV":
        out["disc"]=P.disc_n; out["disc_fail"]=P.disc_fail; out["disc_lat"]=float(np.mean(P.disc_lat)) if P.disc_lat else float("nan")
    return out
if __name__=="__main__":
    import time
    for proto in ("DSDV","AODV"):
        t0=time.time(); r=simulate(proto,30,5,seed=3); print(proto,{k:(round(v,3) if isinstance(v,float) else v) for k,v in r.items()},round(time.time()-t0,1),"s")
