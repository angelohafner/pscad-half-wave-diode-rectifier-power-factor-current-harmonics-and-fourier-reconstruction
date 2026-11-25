"""Prepare the ideal reference or process fresh, phase-aligned PSCAD records."""
import argparse
import json
import re
from pathlib import Path

import numpy as np
import schemdraw
import schemdraw.elements as el

ROOT=Path(__file__).resolve().parent
FREQ=60.0
V=120.0
R=12.0
IP=V*np.sqrt(2)/R
N=50
ANGLE=np.linspace(0,360,1441)
DATA=ROOT/'data'
DATA.mkdir(exist_ok=True)
def reference(a):
    theta=np.deg2rad(ANGLE)
    return np.where((ANGLE>=a)&(ANGLE<180),IP*np.sin(theta),0.0)

def ideal_coeff(a):
    a=np.deg2rad(a)
    def integral(k):
        return np.pi-a if k==0 else (np.exp(-1j*k*np.pi)-np.exp(-1j*k*a))/(-1j*k)
    z=np.array([IP*(integral(h-1)-integral(h+1))/(2j*np.pi) for h in range(N+1)])
    z[0]/=2
    return z

def metrics(c,vr,ir,p):
    phase=-np.angle(c[1])-np.pi/2
    ir1=abs(c[1])/np.sqrt(2)
    q=vr*ir1*np.sin(phase)
    return dict(p=float(p),s=float(vr*ir),q=float(q),ir=float(ir),vr=float(vr),
                pf=float(p/(vr*ir)),phase=float(np.rad2deg(phase)),i1=float(ir1),
                df=float(ir1/ir),disp=float(np.cos(phase)),dc=float(c[0].real),
                d=float(vr*np.sqrt(max(0,ir*ir-ir1*ir1))))
def read_native(folder):
    case='HalfWaveSCR90'
    meta=folder/(case+'.inf')
    cols={name:int(j) for j,name in re.findall(r'PGB\((\d+)\).*?Desc="([^"]+)"',meta.read_text())}
    assert {'Voltage_V','Current_A','Gate'}<=cols.keys(),cols
    records=np.loadtxt(folder/(case+'_01.out'),skiprows=1)
    t=records[:,0];v=records[:,cols['Voltage_V']];i=records[:,cols['Current_A']];g=records[:,cols['Gate']]
    dt=np.median(np.diff(t)); n=round(6/FREQ/dt)
    assert len(t)>n and np.allclose(np.diff(t),dt,atol=1e-9)
    sl=slice(-n-1,-1); omega=2*np.pi*FREQ
    phase=np.angle(np.mean(v[sl]*np.exp(-1j*omega*t[sl])))+np.pi/2
    theta=omega*t[sl]+phase
    c=np.array([np.mean(i[sl]*np.exp(-1j*h*theta))*(2 if h else 1) for h in range(N+1)])
    angles=np.rad2deg((omega*t+phase)%(2*np.pi))
    def edges(x):
        idx=np.flatnonzero(np.diff(x.astype(int))==1)+1
        return idx[t[idx]>.08]
    firing=float(np.median(angles[edges(i>1.)]))
    onset=float(np.median(angles[edges(g>.5)]))
    ir=np.sqrt(np.mean(i[sl]**2));vr=np.sqrt(np.mean(v[sl]**2));p=np.mean(v[sl]*i[sl])
    m=metrics(c,vr,ir,p)
    assert abs(firing-90)<.6 and abs(onset-90)<.6 and abs(m['pf']-.5)<.003 and abs(m['phase']-32.4816)<.3,(firing,onset,m)
    assert abs(p-300)<2 and abs(ir-5)<.03 and abs(m['q']-600/np.pi)<2
    start=(np.floor((omega*t[-1]+phase)/(2*np.pi)+1e-6)-1)*2*np.pi
    times=(start+np.deg2rad(ANGLE)-phase)/omega
    wave=np.interp(times,t,i)
    raw=np.c_[t[sl],v[sl],i[sl],g[sl]]
    np.savez_compressed(DATA/'pscad_samples.npz',samples=raw,columns=['time_s','source_V','current_A','gate_pu'])
    return c,m,wave,np.interp(times,t,g),firing,onset

def draw_circuit():
    with schemdraw.Drawing(show=False,canvas='matplotlib') as drawing:
        drawing.config(unit=2,color='#edf5f8',lw=2.8)
        drawing+=el.SourceSin().up().length(2.5)
        drawing+=el.Line().right().length(.30)
        scr=drawing.add(el.SCR().right().length(2.85).color('#ffb65c'))
        drawing.push()
        drawing+=el.Line().at(scr.gate).down().length(.45).color('#c1adff').dot()
        drawing.pop()
        drawing+=el.Line().right().length(.45)
        drawing+=el.ResistorIEEE().down().length(2.5)
        drawing+=el.Line().left().length(3.6)
        drawing.save(str(DATA/'scr_circuit.png'),transparent=True,dpi=190)

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--native',type=Path); opts=ap.parse_args()
    diode=ideal_coeff(0);scr=ideal_coeff(90)
    m=metrics(scr,V,5,300);wv=reference(90);gate=((ANGLE>=90)&(ANGLE<100)).astype(float)
    f=90.;onset=90.
    if opts.native:
        scr,m,wv,gate,f,onset=read_native(opts.native)
    assert abs(np.angle(diode[1])+np.pi/2)<1.e-10
    assert abs(m['s']**2-(m['p']**2+m['q']**2+m['d']**2))<5
    sample_angles=np.deg2rad(ANGLE)
    y50=np.real(np.exp(1j*sample_angles[:,None]*np.arange(N+1))@scr)
    peak=float(np.max(y50[(ANGLE>=90)&(ANGLE<105)]))
    results=dict(native=bool(opts.native),scr=m,diode=metrics(diode,V,10/np.sqrt(2),600),
                 firing=f,gate_on=onset,co_re=scr.real.tolist(),co_im=scr.imag.tolist(),
                 diode_re=diode.real.tolist(),diode_im=diode.imag.tolist(),
                 angle=ANGLE.tolist(),current=wv.tolist(),gate=gate.tolist(),peak50=peak)
    (DATA/'study.json').write_text(json.dumps(results,separators=(',',':')),encoding='utf-8')
    draw_circuit()
    print('PSCAD measurements' if opts.native else 'Ideal analytical reference',m,flush=True)
