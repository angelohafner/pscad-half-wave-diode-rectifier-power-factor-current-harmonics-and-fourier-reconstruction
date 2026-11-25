"""Compute the GTO case, process PSCAD records, and generate the Schemdraw figure."""
import argparse
import json
import re
from pathlib import Path

import numpy as np
import schemdraw
import schemdraw.elements as el
from schemdraw.segments import Segment

ROOT=Path(__file__).resolve().parent
DATA=ROOT/"data"
PART3=ROOT.parent/"part-3-antiparallel-thyristors"/"data"
VRMS, FREQ, RLOAD = 120.,60.,12.
RON, ROFF = .001,1e8
PEAK=np.sqrt(2)*VRMS/RLOAD
ANGLE=np.linspace(0,360,1441)
ORDERS=np.arange(51)
WINDOWS=((60,120),(240,300))


def coefficients():
    """Exact cosine-reference peak phasors for the gated sinusoid, including the zero DC."""
    a,b=np.deg2rad(WINDOWS[0])
    def integral(k):
        if k==0:
            return b-a
        return (np.exp(-1j*k*b)-np.exp(-1j*k*a))/(-1j*k)
    c=np.zeros(51,dtype=complex)
    for h in ORDERS[1::2]:
        c[h]=PEAK*(integral(h-1)-integral(h+1))/(1j*np.pi)
    c.real=0  # Equal gating about the voltage peaks removes the cosine components.
    return c


def solve():
    per_cycle=7200
    step=np.arange(8*per_cycle)+.5
    t=step/(per_cycle*FREQ)
    angle=step%per_cycle*360/per_cycle
    v=VRMS*np.sqrt(2)*np.sin(np.deg2rad(angle))
    g1,g2=[(angle>=a)&(angle<b) for a,b in WINDOWS]
    # Reverse blocking and two parallel branch conductances are explicit.
    conductance=np.where(g1 & (v>0),1/RON,1/ROFF)+np.where(g2 & (v<0),1/RON,1/ROFF)
    i=v/(RLOAD+1/conductance)
    return np.column_stack((t,v,i,g1,g2))


def read_pscad(folder):
    case="AntiParallelGTO"
    info=(folder/(case+".inf")).read_text()
    records=np.loadtxt(folder/(case+"_01.out"),skiprows=1)
    channels={name:(int(j),unit.lower()) for j,name,unit in re.findall(
        r'PGB\((\d+)\).*?Desc="([^"]+)".*?Units="([^"]*)"',info)}
    indices=[0]
    for name,unit in [("Voltage_V","v"),("Current_A","a"),("Gate1","pu"),("Gate2","pu")]:
        index,actual=channels[name]
        if actual!=unit:
            raise ValueError(f"Unexpected unit for {name}: {actual}")
        indices.append(index)
    return records[:,indices]


def analyze(record):
    t,v,i,g1,g2=record.T
    dt=np.median(np.diff(t))
    n=round(6/(FREQ*dt))
    if n<1200 or len(t)<n+2 or not np.allclose(np.diff(t),dt,rtol=1e-6,atol=1e-10) or abs(n*FREQ*dt-6)>1e-5:
        raise ValueError("Expected six complete steady-state cycles at a uniform time step")
    win=slice(-n-1,-1)
    omega=2*np.pi*FREQ
    phase=np.angle(np.mean(v[win]*np.exp(-1j*omega*t[win])))+np.pi/2
    theta=omega*t+phase
    degree=np.rad2deg(theta)%360
    for signal,limits in [(g1>.5,WINDOWS[0]),(i>1.,WINDOWS[0]),(g2>.5,WINDOWS[1]),(i< -1.,WINDOWS[1])]:
        for diff,expected in zip([1,-1],limits):
            ix=np.flatnonzero(np.diff(signal.astype(int))==diff)+1
            ix=ix[(ix>=len(t)-n-1)&(ix<len(t)-1)]
            if len(ix)!=6 or max(abs(degree[ix]-expected))>.6:
                raise ValueError(f"Switching edge at {expected} degrees failed: {degree[ix]}")
    vr=np.sqrt(np.mean(v[win]**2))
    ir=np.sqrt(np.mean(i[win]**2))
    p=np.mean(v[win]*i[win])
    c1=2*np.mean(i[win]*np.exp(-1j*theta[win]))
    i1=abs(c1)/np.sqrt(2)
    phi=-np.angle(c1)-np.pi/2
    values=dict(vr=vr,ir=ir,p=p,s=vr*ir,load_p=RLOAD*ir**2,pf=p/(vr*ir),dc=np.mean(i[win]),
                lag=np.rad2deg(phi),i1=i1,q1=vr*i1*np.sin(phi),displacement=np.cos(phi),distortion=i1/ir)
    if abs(values["pf"]-.78038)>.003 or abs(values["lag"])>.3 or abs(p-730.8)>3:
        raise ValueError(f"Unexpected source-port measurements {values}")
    start=(np.floor(theta[-1]/(2*np.pi))-1)*2*np.pi
    probe=(start+np.deg2rad(ANGLE)-phase)/omega
    return values,np.interp(probe,t,i)


class GateTurnOff(el.SCR):
    """Add the turn-off cross-stroke to the thyristor gate lead."""
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        gx,gy=self.anchors["gate"]
        self.segments.append(Segment([(gx-.26,gy+.23),(gx-.06,gy+.43)]))


def draw():
    with schemdraw.Drawing(show=False,canvas="matplotlib") as d:
        d.config(color="#f2f5f8",lw=2.4,unit=2)
        d+=el.SourceSin().at((0,0)).to((0,2))
        d+=el.Line().to((1.1,2)).dot()
        for y,direction,color in [(2.92,1,"#ffba68"),(1.08,-1,"#68dfc8")]:
            d+=el.Line().at((1.1,2)).to((1.1,y))
            a,b=(1.1,4.) if direction==1 else (4.,1.1)
            device=d.add(GateTurnOff().at((a,y)).to((b,y)).color(color))
            xg,yg=device.gate
            d+=el.Line().at((xg,yg)).to((xg+.19*direction,yg-.20*direction)).color(color).dot()
            d+=el.Line().at((4.,y)).to((4.,2))
        d+=el.Dot().at((4.,2))
        d+=el.Line().at((4.,2)).to((5.2,2))
        d+=el.ResistorIEEE().to((5.2,0))
        d+=el.Line().to((0,0))
        d.save(str(DATA/"gto_circuit.png"),dpi=200,transparent=True)


def prepare(native):
    DATA.mkdir(exist_ok=True)
    record=read_pscad(native) if native else solve()
    m,current=analyze(record)
    reference=json.loads((PART3/"results.json").read_text())
    with np.load(PART3/"waveforms.npz") as scr:
        np.savez_compressed(DATA/"waveforms.npz",angle=ANGLE,current=current,c=coefficients(),scr=scr["pair"],scr_c=scr["c_pair"])
    out=dict(source="PSCAD" if native else "Python switch model",gto=m,scr=reference["pair"],scr_source=reference["source"])
    (DATA/"results.json").write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    if native:
        np.savez_compressed(DATA/"pscad_record.npz",record=record,columns=["s","V","A","gate1","gate2"])
    draw()
    print(json.dumps(out,indent=2))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--native",type=Path,help="PSCAD build directory containing the .inf and .out files")
    prepare(parser.parse_args().native)
