"""Compare source-port recordings, a latched-switch circuit model, and exact Fourier coefficients."""
import argparse
import json
import re
from pathlib import Path

import numpy as np
import schemdraw
import schemdraw.elements as el

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
FREQ, VRMS, RLOAD = 60.0, 120.0, 12.0
RON, ROFF = 0.001, 1e8
PEAK = np.sqrt(2) * VRMS / RLOAD
ORDERS = np.arange(51)
ANGLE = np.linspace(0, 360, 1441)


def coefficients(alpha):
    """Cosine-reference peak phasors for conduction from alpha to pi."""
    def integral(k):
        if k == 0:
            return np.pi - alpha
        return (np.exp(-1j*k*np.pi) - np.exp(-1j*k*alpha)) / (-1j*k)
    result = np.array([PEAK*(integral(h-1)-integral(h+1))/(2j*np.pi) for h in ORDERS])
    result[0] /= 2
    result[abs(result) < 1e-12] = 0
    return result


def circuit_samples():
    """Time-step two gated, latching conductances in parallel with opposite polarity."""
    per_cycle = 7200
    t = (np.arange(8*per_cycle)+0.5)/(FREQ*per_cycle)
    theta = (np.arange(len(t)) % per_cycle + 0.5)*360/per_cycle
    voltage = np.sqrt(2)*VRMS*np.sin(np.deg2rad(theta))
    gp = (theta >= 90) & (theta < 100)
    gn = (theta >= 270) & (theta < 280)
    current = np.empty_like(voltage)
    positive = negative = False
    for k, v in enumerate(voltage):
        positive = v > 0 and (positive or gp[k])
        negative = v < 0 and (negative or gn[k])
        conductance = (1/RON if positive else 1/ROFF) + (1/RON if negative else 1/ROFF)
        current[k] = v/(RLOAD+1/conductance)
    return np.column_stack((t, voltage, current, gp, gn))


def native_samples(folder, name, channels):
    meta = (folder / (name+".inf")).read_text()
    signals = {key: (int(idx), unit) for idx, key, unit in re.findall(
        r'PGB\((\d+)\).*?Desc="([^"]+)".*?Units="([^"]*)"', meta)}
    values = np.loadtxt(folder / (name+"_01.out"), skiprows=1)
    indices = [0]
    for key, unit in channels:
        idx, actual_unit = signals[key]
        if actual_unit.lower() != unit.lower():
            raise ValueError(f"{key} has units {actual_unit}; expected {unit}")
        indices.append(idx)
    return values[:, indices]


def analyze(samples):
    t, v, i = samples[:, :3].T
    dt = np.median(np.diff(t))
    count = round(6 / (FREQ * dt))
    if len(t) < count+2 or abs(count*dt*FREQ-6)>1e-5 or not np.allclose(np.diff(t),dt,atol=1e-10,rtol=1e-6):
        raise ValueError("Expected six complete uniformly sampled steady-state cycles")
    win = slice(-count-1, -1)
    omega = 2*np.pi*FREQ
    phase = np.angle(np.mean(v[win]*np.exp(-1j*omega*t[win])))+np.pi/2
    angles = omega*t+phase
    c = np.array([np.mean(i[win]*np.exp(-1j*h*angles[win]))*(2 if h else 1) for h in ORDERS])
    vr = np.sqrt(np.mean(v[win]**2))
    ir = np.sqrt(np.mean(i[win]**2))
    power = np.mean(v[win]*i[win])
    phi = -np.angle(c[1])-np.pi/2
    i1 = abs(c[1])/np.sqrt(2)
    values = dict(p=power,s=vr*ir,ir=ir,vr=vr,pf=power/(vr*ir),dc=c[0].real,
                  lag=np.rad2deg(phi),displacement=np.cos(phi),distortion=i1/ir,
                  q1=vr*i1*np.sin(phi),i1=i1)
    # Keep the final complete cycle, aligned to the source voltage's rising zero.
    start = (np.floor(angles[-1]/(2*np.pi))-1)*2*np.pi
    probe = (start+np.deg2rad(ANGLE)-phase)/omega
    trace = np.interp(probe,t,i)
    if samples.shape[1] == 5:
        for gate, conduction, nominal in [(samples[:,3], i>1, 90), (samples[:,4], i< -1, 270)]:
            for state in [gate>.5, conduction]:
                rising = np.flatnonzero(np.diff(state.astype(int))==1)+1
                edges = np.mod(np.rad2deg(angles[rising][t[rising]>=t[win][0]]),360)
                if len(edges)<5 or max(abs(edges-nominal))>.6:
                    raise ValueError(f"Unexpected switching near {nominal} degrees: {edges}")
        if abs(values["pf"]-1/np.sqrt(2))>.003 or abs(values["dc"])>.02 or abs(values["lag"]-32.4816)>.3:
            raise ValueError(f"Unexpected symmetrical controller metrics {values}")
    return values, trace


def schematic():
    inks = dict(line="#f2f5f8", plus="#ffba68", minus="#68dfc8")
    with schemdraw.Drawing(show=False,canvas="matplotlib") as d:
        d.config(color=inks["line"],lw=2.4,unit=2)
        d += el.SourceSin().at((0,0)).to((0,2))
        d += el.Line().to((1.1,2)).dot()
        for y, forward, color in [(2.9,True,inks["plus"]),(1.1,False,inks["minus"])]:
            d += el.Line().at((1.1,2)).to((1.1,y))
            start,end = ((1.1,y),(4.0,y)) if forward else ((4.0,y),(1.1,y))
            scr = d.add(el.SCR().at(start).to(end).color(color))
            # Extend each device gate from its Schemdraw anchor.
            point = scr.gate
            d += el.Line().at(point).to((point.x + (.20 if forward else -.20), point.y + (-.32 if forward else .32))).color(color).dot()
            d += el.Line().at((4.0,y)).to((4.0,2))
        d += el.Dot().at((4,2))
        d += el.Line().at((4,2)).to((5.1,2))
        d += el.ResistorIEEE().to((5.1,0))
        d += el.Line().to((0,0))
        d.save(str(DATA/"antiparallel.png"),dpi=200,transparent=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--native",type=Path,help="PSCAD build directory containing the Part 3 .inf and .out files")
    args=parser.parse_args()
    DATA.mkdir(exist_ok=True)
    main_channels=[("Voltage_V","V"),("Current_A","A")]
    diode=native_samples(ROOT.parent/"pscad/HalfWaveDiode.gf81","HalfWaveDiode",main_channels)
    source="PSCAD" if args.native else "Python switch model"
    pair=(native_samples(args.native,"AntiParallelSCR90",main_channels+[("Gate1","pu"),("Gate2","pu")])
          if args.native else circuit_samples())
    diode_m, diode_trace = analyze(diode)
    pair_m, pair_trace = analyze(pair)
    single=coefficients(np.pi/2)
    exact=single*(1-(-1.)**ORDERS)
    np.savez_compressed(DATA/"waveforms.npz", angle=ANGLE,pair=pair_trace,diode=diode_trace,
                        c_pair=exact,c_single=single,c_diode=coefficients(0))
    output=dict(pair=pair_m, diode=diode_m, source=source)
    (DATA/"results.json").write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
    schematic()
    print(json.dumps(output,indent=2))

if __name__=="__main__":
    main()
