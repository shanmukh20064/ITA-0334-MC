import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np
from matplotlib.patches import FancyBboxPatch, Circle
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":8})
BL="#2F5496";OR="#C55A11";GR="#548235";GY="#7F7F7F";LB="#DCE6F5";LO="#FBE5D6";LG="#E2EFDA"
def fig(w=7.2,h=3.6):
    f,a=plt.subplots(figsize=(w,h)); a.axis("off"); a.set_aspect("equal"); return f,a
def box(a,x,y,w,h,t,fc=LB,ec=BL,fs=7.5,bold=False):
    a.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.03",fc=fc,ec=ec,lw=1)); a.text(x+w/2,y+h/2,t,ha="center",va="center",fontsize=fs,fontweight="bold" if bold else "normal")
def node(a,x,y,t,c=BL,r=.28,fs=7):
    a.add_patch(Circle((x,y),r,fc="white",ec=c,lw=1.4,zorder=5)); a.text(x,y,t,ha="center",va="center",fontsize=fs,color=c,fontweight="bold",zorder=6)
def line(a,p,q,c=GY,ls="-",lw=1,arrow=False):
    a.annotate("",xy=q,xytext=p,arrowprops=dict(arrowstyle="->" if arrow else "-",color=c,lw=lw,ls=ls))
def save(f,n): f.savefig(f"../img/{n}.png",dpi=200,bbox_inches="tight"); plt.close(f)
# ---- Q1 architecture
f,a=fig(7.4,4.0); a.set_xlim(0,12); a.set_ylim(-1.2,6)
for x,y,t in ((1.2,1.0,"MN1\nphone"),(3.2,0.8,"MN2\nlaptop"),(5.2,1.0,"MN3\nsensor"),(8.4,0.9,"MN4\nvehicle"),(10.8,1.2,"MN5\ntablet")):
    node(a,x,y,t,OR,.45,6)
for cx,t in ((2.9,"AP1"),(9.6,"AP2")):
    a.add_patch(Circle((cx,1.3),2.2,fc=LG,ec=GR,alpha=.35,lw=1,ls="--")); box(a,cx-.5,2.55,1.0,.55,t+"\n(base station)",LG,GR,6.5)
for (x,y,ap) in ((1.2,1.0,2.9),(3.2,0.8,2.9),(5.2,1.0,2.9),(8.4,0.9,9.6),(10.8,1.2,9.6)):
    line(a,(x,y+.45),(ap,2.55),OR,"--",1.2)
box(a,4.6,4.0,2.8,.7,"Switch / access router",LB,BL,7.5)
line(a,(2.9,3.1),(5.3,4.0),BL,"-",1.8); line(a,(9.6,3.1),(6.7,4.0),BL,"-",1.8)
box(a,0.6,5.0,2.6,.7,"Authentication / DHCP",LB,BL,7); box(a,4.7,5.0,2.6,.7,"Internet / core",LB,BL,7.5); box(a,8.8,5.0,2.6,.7,"Application server",LB,BL,7)
line(a,(6.0,4.7),(6.0,5.0),BL,"-",1.8); line(a,(4.6,4.35),(1.9,5.0),BL,"-",1); line(a,(7.4,4.35),(10.1,5.0),BL,"-",1)
a.text(5.9,-1.05,"- - -  wireless link (shared, lossy, limited bandwidth)      ——  wired backbone",fontsize=6.5,color=GY,va="center")
save(f,"f1_arch")
# ---- Q2 Mobile IP architecture
f,a=fig(7.4,3.4); a.set_xlim(0,12); a.set_ylim(0,5.6)
box(a,0.3,3.6,2.6,1.4,"HOME NETWORK\n10.1.1.0/24\nHome Agent HA\n10.1.1.1",LB,BL,7.5)
box(a,9.1,3.6,2.6,1.4,"FOREIGN NETWORK\n192.168.2.0/24\nForeign Agent FA\nCoA 192.168.2.1",LO,OR,7.5)
box(a,4.7,4.0,2.6,.9,"Internet / IP backbone",LG,GR,8)
box(a,4.7,1.5,2.6,.9,"Correspondent Node CN\n172.16.5.9",LG,GR,7.5)
node(a,10.4,0.9,"MN\n10.1.1.50",OR,.6,6.5)
line(a,(2.9,4.3),(4.7,4.4),BL,"-",1.8); line(a,(7.3,4.4),(9.1,4.3),BL,"-",1.8); line(a,(6.0,2.4),(6.0,4.0),BL,"-",1.8)
line(a,(10.4,1.5),(10.4,3.6),OR,"--",1.4)
a.annotate("",xy=(9.1,4.9),xytext=(2.9,4.9),arrowprops=dict(arrowstyle="->",color=OR,lw=1.6,connectionstyle="arc3,rad=-0.15"))
a.text(6.0,5.45,"IP-in-IP tunnel  HA -> FA (CoA)",ha="center",color=OR,fontsize=7.5)
a.text(0.3,3.1,"1  CN sends to home address 10.1.1.50",ha="left",fontsize=7); a.text(0.3,2.7,"2  HA intercepts, encapsulates, tunnels to CoA",ha="left",fontsize=7); a.text(0.3,2.3,"3  FA decapsulates, delivers to the MN",ha="left",fontsize=7)
a.text(9.0,0.4,"MN moved here; home address stays 10.1.1.50",fontsize=6.5,color=OR,ha="center",x=None) if False else a.text(8.2,0.35,"MN has moved here; its home\naddress stays 10.1.1.50",fontsize=6.5,color=OR,ha="center")
save(f,"f2_arch")
# ---- Q2 sequence diagram
f,a=plt.subplots(figsize=(7.4,4.1)); a.axis("off"); a.set_xlim(0,12); a.set_ylim(0,8.4)
cols=[("MN",1.0),("New FA",3.7),("Old FA",6.3),("HA",8.8),("CN",11.0)]
for n,x in cols:
    a.text(x,8.1,n,ha="center",fontweight="bold",fontsize=8,color=BL); a.plot([x,x],[0.2,7.8],color=GY,lw=.8,ls=":")
def msg(y,x1,x2,t,c=BL):
    a.annotate("",xy=(x2,y),xytext=(x1,y),arrowprops=dict(arrowstyle="->",color=c,lw=1.2)); a.text((x1+x2)/2,y+.13,t,ha="center",fontsize=6.3,color=c)
x={n:v for n,v in cols}
msg(7.4,x["CN"],x["HA"],"data to 10.1.1.50",GR); msg(7.0,x["HA"],x["Old FA"],"tunnel (CoA = old FA)",OR)
a.text(x["MN"]-0.9,6.75,"MN moves: L2 handoff (about 100 ms)",fontsize=6.3,color=OR,ha="left")
msg(6.0,x["New FA"],x["MN"],"1 Agent advertisement (every 1 s)"); msg(5.4,x["MN"],x["New FA"],"2 Registration request (home addr, HA, lifetime, ID)")
msg(4.8,x["New FA"],x["HA"],"3 Request relayed (+ auth MN-HA)"); a.text(x["HA"]+0.1,4.35,"4 HA updates binding\nhome addr -> new CoA",fontsize=6.3,ha="left",color=BL)
msg(3.6,x["HA"],x["New FA"],"5 Registration reply"); msg(3.0,x["New FA"],x["MN"],"6 Reply relayed: registered")
msg(2.4,x["CN"],x["HA"],"data to 10.1.1.50",GR); msg(2.0,x["HA"],x["New FA"],"tunnel (CoA = new FA)",OR); msg(1.5,x["New FA"],x["MN"],"decapsulated delivery",GR)
a.text(x["Old FA"],6.45,"packets arriving\nhere are lost",fontsize=6.3,color=OR,ha="center")
save(f,"f2_seq")
# ---- Q3 comparison diagram
f,(a1,a2)=plt.subplots(1,2,figsize=(7.4,3.4)); 
for a in (a1,a2): a.axis("off"); a.set_aspect("equal")
a1.set_xlim(-0.5,6.5); a1.set_ylim(-0.3,6.4); a1.set_title("Cellular (infrastructure-based)",fontsize=8,fontweight="bold",color=BL)
BSs=[(1.5,4.4),(4.5,4.4),(3.0,1.8)]
for bx,by in BSs: a1.add_patch(Circle((bx,by),1.7,fc=LB,ec=BL,alpha=.35,ls="--")); box(a1,bx-.3,by-.18,.6,.36,"BS",BL,BL,6.5); a1.texts[-1].set_color("w")
box(a1,2.5,0.2,1.0,.5,"MSC / core",LG,GR,6.5)
for bx,by in BSs: line(a1,(bx,by-.2),(3.0,.7),BL,"-",1.2)
for (x,y) in ((.9,4.8),(2.0,3.8),(4.2,5.0),(5.0,3.9),(2.5,1.5),(3.7,2.1)): node(a1,x,y,"",OR,.14); 
line(a1,(2.0,3.8),(1.5,4.2),OR,"--"); line(a1,(5.0,3.9),(4.5,4.2),OR,"--"); line(a1,(2.5,1.5),(3.0,1.8),OR,"--")
a1.text(3.0,5.85,"users talk only via a base station",ha="center",fontsize=6.5,color=GY)
a2.set_xlim(-0.5,6.5); a2.set_ylim(-0.3,6.4); a2.set_title("Ad hoc (infrastructure-less, multi-hop)",fontsize=8,fontweight="bold",color=OR)
P={"S":(0.6,3.0),"a":(1.9,4.4),"b":(2.2,1.7),"c":(3.4,3.4),"d":(4.4,4.7),"e":(4.6,2.2),"D":(5.5,3.4)}
for u,v in (("S","a"),("S","b"),("a","c"),("b","c"),("c","d"),("c","e"),("d","D"),("e","D")): line(a2,P[u],P[v],GY,"-",1)
for u,v in (("S","a"),("a","c"),("c","e"),("e","D")): line(a2,P[u],P[v],OR,"-",2.4)
for k,(x,y) in P.items(): node(a2,x,y,k if k in "SD" else "",OR if k in "SD" else BL,.22,7)
a2.text(3.0,0.4,"route S -> a -> c -> e -> D (nodes relay for each other)",ha="center",fontsize=6.5,color=GY)
f.tight_layout(); save(f,"f3_diag")
# ---- Q4 application architecture
f,a=fig(7.4,3.6); a.set_xlim(0,12); a.set_ylim(0,6)
box(a,0.2,4.1,3.3,1.5,"AMBULANCE (Mobile Node)\npatient monitor + tablet + radio\nhome address 10.1.1.50\nMN software: registration, keys",LO,OR,7)
for x,t in ((4.2,"Cell tower 1\nFA 1"),(6.4,"Cell tower 2\nFA 2"),(8.6,"Cell tower 3\nFA 3")): box(a,x,2.4,1.8,.9,t,LB,BL,7)
for x in (5.1,7.3,9.5): line(a,(3.5,4.6),(x,3.3),OR,"--",1.2)
box(a,0.2,0.2,3.0,1.2,"HOME AGENT (hospital A)\n10.1.1.1, binding table,\nauthentication server",LB,BL,7)
box(a,4.6,0.2,3.2,1.2,"Operator IP core / Internet\ntunnel HA <-> FA",LG,GR,7.5)
box(a,8.8,0.2,3.0,1.2,"CORRESPONDENT NODE\nspecialist doctor / hospital B\nEHR server",LG,GR,7)
for x in (5.1,7.3,9.5): line(a,(x,2.4),(6.2,1.4),BL,"-",1.4)
line(a,(4.6,0.8),(3.2,0.8),BL,"-",1.8); line(a,(7.8,0.8),(8.8,0.8),BL,"-",1.8)
a.text(8.3,5.15,"Backup link (satellite / second SIM)\nused in coverage holes",ha="center",fontsize=6.8,color=OR)
line(a,(3.5,5.2),(6.1,5.2),OR,":",1.4)
save(f,"f4_arch")
# ---- Q5 topology
f,(a1,a2)=plt.subplots(1,2,figsize=(7.4,2.9))
Pn={"A":(0.5,1.5),"B":(1.7,1.5),"C":(2.9,2.6),"D":(4.2,2.6),"E":(2.9,0.4),"F":(4.2,0.4)}
ed=[("A","B"),("B","C"),("C","D"),("B","E"),("E","D"),("E","F")]
for a,ttl,broken in ((a1,"Before: A to F = A-B-E-F (3 hops)",False),(a2,"After link B-E fails: A to F = A-B-C-D-E-F (5 hops)",True)):
    a.axis("off"); a.set_aspect("equal"); a.set_xlim(-0.2,4.8); a.set_ylim(-0.4,3.2); a.set_title(ttl,fontsize=7.5,fontweight="bold")
    for u,v in ed:
        if broken and {u,v}=={"B","E"}: line(a,Pn[u],Pn[v],OR,":",1.6); a.text(2.1,1.0,"X",color=OR,fontsize=14,fontweight="bold",ha="center"); continue
        line(a,Pn[u],Pn[v],GY,"-",1)
    path=[("A","B"),("B","C"),("C","D"),("D","E"),("E","F")] if broken else [("A","B"),("B","E"),("E","F")]
    for u,v in path: line(a,Pn[u],Pn[v],BL,"-",2.6)
    for k,(x,y) in Pn.items(): node(a,x,y,k,BL if k not in "AF" else OR,.22,8)
f.tight_layout(); save(f,"f5_topo")
# ---- Q6 AODV discovery
f,a=fig(7.4,3.3); a.set_xlim(0,12); a.set_ylim(0,5.6)
Q={"S":(0.9,2.8),"1":(3.0,4.4),"2":(3.0,1.2),"3":(5.2,2.8),"4":(7.4,4.4),"5":(7.4,1.2),"D":(10.2,2.8)}
for u,v in (("S","1"),("S","2"),("1","3"),("2","3"),("3","4"),("3","5"),("4","D"),("5","D"),("1","4")): line(a,Q[u],Q[v],"#BBBBBB","-",1)
for u,v in (("S","1"),("S","2"),("1","3"),("2","3"),("3","4"),("3","5"),("4","D"),("5","D"),("1","4")): pass
for u,v in (("S","1"),("S","2"),("1","3"),("2","3"),("3","4"),("3","5"),("4","D"),("5","D")): line(a,Q[u],Q[v],BL,"-",.8)
for u,v in (("D","4"),("4","3"),("3","1"),("1","S")): a.annotate("",xy=Q[v],xytext=Q[u],arrowprops=dict(arrowstyle="->",color=OR,lw=2.4,shrinkA=9,shrinkB=9))
for k,(x,y) in Q.items(): node(a,x,y,k,OR if k in "SD" else BL,.3,8)
a.text(6.0,5.3,"RREQ (blue): S floods to neighbours, each node rebroadcasts once; reverse route is stored at each node",ha="center",fontsize=7,color=BL)
a.text(6.0,0.15,"RREP (orange): D replies by unicast along the reverse path S<-1<-3<-4<-D; forward route installed. RERR: sent upstream if a link on this path breaks",ha="center",fontsize=6.6,color=OR)
save(f,"f6_aodv")
# ---- Q7 final design
f,a=fig(7.6,4.4); a.set_xlim(0,13); a.set_ylim(0,7.6)
a.add_patch(FancyBboxPatch((0.2,0.4),8.3,6.2,boxstyle="round,pad=0.05",fc="#FFF9E5",ec=OR,ls="--",lw=1.2)); a.text(0.5,6.3,"DISASTER ZONE: self-organising wireless mesh (AODV routing)",fontsize=7.5,color=OR,fontweight="bold")
M={"amb1":(1.4,4.6),"amb2":(3.4,5.4),"pol":(5.4,5.0),"res1":(2.0,2.4),"res2":(4.2,3.2),"med":(6.2,2.2),"gw":(7.6,3.9),"res3":(4.0,1.0)}
for u,v in (("amb1","amb2"),("amb2","pol"),("amb1","res1"),("res1","res2"),("amb2","res2"),("res2","pol"),("res2","med"),("pol","gw"),("med","gw"),("res1","res3"),("res3","res2")): line(a,M[u],M[v],GY,"-",1)
for k,(x,y) in M.items(): node(a,x,y,k if k!="gw" else "FA",OR if k=="gw" else BL,.42,6.5 if k=="gw" else 5.8)
box(a,9.6,5.2,3.2,1.0,"Satellite / surviving tower\n(uplink backhaul)",LG,GR,7); box(a,9.6,3.6,3.2,1.1,"Internet / operator core\ntunnel FA <-> HA",LB,BL,7)
box(a,9.6,1.7,3.2,1.1,"HOME AGENT + command\ncentre, hospital servers (CN)",LB,BL,6.5)
line(a,(8.0,3.95),(9.6,5.8),GR,"-",2); line(a,(11.2,5.4),(11.2,4.7),GR,"-",2); line(a,(11.2,3.6),(11.2,2.8),BL,"-",2)
a.text(11.2,7.2,"Mobile IP: MN keeps its home address;\nthe FA registers it with the HA",fontsize=6.6,color=OR,ha="center")
a.text(6.5,0.1,"inside the zone: AODV routes data hop by hop; store-carry-forward when partitioned",fontsize=6.6,color=GY,ha="center")
save(f,"f7_arch")
print("diagrams ok")
