"""Prepare source-aligned waveform, spectrum, and Fourier series data for the film."""
from pathlib import Path
import json
import re
import numpy as np
import schemdraw
import schemdraw.elements as el

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'assets'
ASSETS.mkdir(exist_ok=True)
FREQ = 60
SAMPLES = 2000

def native_record(case):
    folder = ROOT / 'pscad'
    candidates = list(folder.glob(f'{case}.*/{case}.inf'))
    if len(candidates) != 1:
        raise RuntimeError(f'Expected one fresh native output for {case}, found {candidates}')
    meta = candidates[0]
    entries = re.findall(r'PGB\((\d+)\).*?Desc="([^"]+)".*?Units="([^"]+)"', meta.read_text())
    cols = {name: int(index) for index, name, unit in entries if (name,unit) in [('Voltage_V','V'),('Current_A','A')]}
    record = np.loadtxt(meta.with_name(case+'_01.out'), skiprows=1)
    return record[:, 0],record[:,cols['Voltage_V']],record[:,cols['Current_A']]

def analyze(t,v,i):
    dt=np.median(np.diff(t))
    n=round(0.1/dt)
    assert np.allclose(n*dt,0.1,atol=1e-8) and np.allclose(np.diff(t),dt,atol=2e-8)
    # Use a half-open window containing exactly six full cycles.
    vwin=v[-n-1:-1]; iwin=i[-n-1:-1]; win=t[-n-1:-1]
    w=2*np.pi*FREQ
    phase=np.angle(np.mean(vwin*np.exp(-1j*w*win)))+np.pi/2
    theta=w*win+phase
    coef=np.array([np.mean(iwin*np.exp(-1j*h*theta)) for h in range(51)])
    coef[1:]*=2
    rms=lambda x:float(np.sqrt(np.mean(x*x)))
    p=float(np.mean(vwin*iwin)); vr=rms(vwin); ir=rms(iwin)
    ir1=abs(coef[1])/np.sqrt(2); spectral_rms=np.abs(coef)/np.sqrt(2); spectral_rms[0]=abs(coef[0])
    phi=float(np.angle(coef[1])+np.pi/2)
    thd=np.linalg.norm(spectral_rms[2:])/ir1
    # Get one actual cycle aligned to the rising voltage zero crossing.
    zero=(np.floor((w*t[-1]+phase)/(2*np.pi)+1e-8)-1)*2*np.pi
    theta_plot=np.linspace(0,2*np.pi,SAMPLES+1)
    times=(zero+theta_plot-phase)/w
    wave=np.interp(times,t,i); volts=np.interp(times,t,v)
    rebuilt=coef[0].real+np.real(np.exp(1j*theta[:,None]*np.arange(1,51))@coef[1:])
    products={}
    for h in (0,1,2,4):
        component=np.real(coef[h]*np.exp(1j*h*theta))
        contribution=vwin*component
        # Average the six measured cycle integrals to get joules per cycle.
        positive_j=float(np.mean(np.maximum(contribution,0)) / FREQ)
        negative_j=float(np.mean(np.minimum(contribution,0)) / FREQ)
        average=float(np.mean(contribution))
        assert np.isclose((positive_j+negative_j)*FREQ,average,atol=1.e-9)
        products[str(h)]=dict(mean=average,positive_j=positive_j,negative_j=negative_j)
    q1=-vr*ir1*np.sin(phi)
    residual_va=vr*np.sqrt(max(0,ir**2-ir1**2))
    assert np.isclose(p,products['1']['mean'],atol=.002)
    assert max(abs(products[str(h)]['mean']) for h in (0,2,4)) < .002
    assert np.isclose((vr*ir)**2,p**2+q1**2+residual_va**2,rtol=1e-6)
    return dict(p=p,s=vr*ir,vr=vr,ir=ir,pf=p/(vr*ir),dc=float(coef[0].real),i1=ir1,df=ir1/ir,
                q1=q1,residual_va=residual_va,products=products,
                dpf=np.cos(phi),thd=thd,err=rms(rebuilt-iwin),re=coef.real.tolist(),im=coef.imag.tolist(),
                spectrum=spectral_rms.tolist(),wave=wave.tolist(),volts=volts.tolist())

def drawing(rectified):
    c='#ffb65c' if rectified else '#62e0cb'
    with schemdraw.Drawing(show=False,canvas='matplotlib',file=None) as d:
        d.config(unit=2,color='#ecf5f8',lw=2.6)
        d += el.SourceSin().up().length(2.4)
        d += el.Line().right().length(0.9)
        d += (el.Diode().color(c) if rectified else el.Line().color(c)).right().length(1.5)
        d += el.Line().right().length(.9)
        d += el.ResistorIEEE().down().length(2.4)
        d += el.Line().left().length(3.3)
        d.save(str(ASSETS/('diode.png' if rectified else 'direct.png')),transparent=True,dpi=210)

if __name__=='__main__':
    records=[native_record(c) for c in ['DirectResistor','HalfWaveDiode']]
    result={'native':True}
    for diode,record in enumerate(records):
        case=analyze(*record)
        assert abs(case['vr']-120)<.1 and abs(case['pf']-[1,1/np.sqrt(2)][diode])<.002
        assert abs(case['dc']-[0,10*np.sqrt(2)/np.pi][diode])<.015
        assert case['err']<.03 and abs(case['pf']-case['dpf']*case['df'])<.0001
        drawing(bool(diode))
        result[['direct','diode'][diode]]=case
        print({k:round(case[k],5) for k in ['p','s','pf','vr','ir','dc','thd','err']})
    (ASSETS/'data.json').write_text(json.dumps(result),encoding='utf-8')

