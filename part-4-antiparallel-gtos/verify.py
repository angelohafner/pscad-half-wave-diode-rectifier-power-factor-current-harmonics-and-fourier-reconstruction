"""Check native wiring, independent Fourier integrals, numerical measurements, and encoded media."""
import argparse
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from study import ANGLE, DATA, ROOT, PEAK

NAME="AntiParallelGTO"
MOVIE=ROOT/"GTO_Gate_Turn_Off_and_Power_Factor.mp4"


def param(element, key):
    return element.find(f"./paramlist/param[@name='{key}']").get("value")


def wiring():
    project=ET.parse(ROOT/"pscad/Part4_GTO_60_120.pswx").findall("projects/project")
    assert len(project)==1 and project[0].get("name")==NAME
    case=ET.parse(ROOT/"pscad"/project[0].get("filepath").replace("\\","/"))
    main=case.find(".//Definition[@name='Main']/schematic")
    switches=main.findall("User[@defn='master:peswitch']")
    assert [(param(s,"Name"),s.get("orient"),param(s,"Type"),param(s,"INTR")) for s in switches]==[
        ("GTO1","1","2","0"),("GTO2","3","2","0")]
    graph={}
    for wire in main.findall("Wire[@classid='WireOrthogonal']"):
        x,y=int(wire.get("x")),int(wire.get("y"))
        points=[(x+int(v.get("x")),y+int(v.get("y"))) for v in wire.findall("vertex")]
        for a,b in zip(points,points[1:]):
            assert a[0]==b[0] or a[1]==b[1]
            graph.setdefault(a,set()).add(b)
            graph.setdefault(b,set()).add(a)
    def connected(start):
        seen,stack={start},[start]
        while stack:
            for p in graph.get(stack.pop(),set())-seen:
                seen.add(p)
                stack.append(p)
        return seen
    # Installed Master Library pins: DP at the origin, DN (0,-36), APUL (36,-36).
    assert {(432,198),(432,90)} <= connected((324,198))
    assert {(468,198),(468,90)} <= connected((612,324))
    assert connected((324,198)).isdisjoint(connected((612,324)))
    assert (522,234) in connected((468,234)) and (378,54) in connected((432,54))
    labels=main.findall("User[@defn='master:datalabel']")
    for coords,tag in [((522,234),"GatePos"),((1044,558),"GatePos"),((378,54),"GateNeg"),((1044,702),"GateNeg")]:
        assert any((int(e.get("x")),int(e.get("y")))==coords and param(e,"Name")==tag for e in labels)
    for e,low,high in [("PeakGate",60,120),("NegativePeakGate",240,300)]:
        code=case.find(f".//Definition[@name='{e}']/script/segment").text
        assert f".GE. {low}.0" in code and f".LT. {high}.0" in code
        assert main.find(f"User[@defn='{NAME}:{e}']") is not None
    assert {param(e,"Name") for e in main.findall("User[@defn='master:pgb']")}>={
        "Gate1","Gate2","Current_A","Voltage_V"}


def electrical():
    study=json.loads((DATA/"results.json").read_text())
    m=study["gto"]
    factor=1/3+np.sqrt(3)/(2*np.pi)
    assert abs(m["pf"]-np.sqrt(factor))<.003 and abs(m["p"]-1200*factor)<3
    assert abs(m["ir"]-10*np.sqrt(factor))<.03 and abs(m["s"]-1200*np.sqrt(factor))<3
    assert abs(m["q1"])<3 and abs(m["dc"])<.02 and abs(m["lag"])<.3
    assert abs(m["pf"]-m["distortion"]*m["displacement"])<.002
    assert abs(m["load_p"]-m["ir"]**2*12)<1e-7
    assert abs(study["scr"]["pf"]-1/np.sqrt(2))<.003
    # Independent midpoint quadrature; align switching times on bin boundaries.
    n=6*32768
    theta=(np.arange(n)+.5)*2*np.pi/n
    local=theta%np.pi
    u=120*np.sqrt(2)*np.sin(theta)
    i=np.where((local>=np.pi/3)&(local<2*np.pi/3),u/12,0.)
    p_ideal=np.mean(i*i*12)
    assert abs(p_ideal-1200*factor)<1e-5
    assert abs((p_ideal-600)/60-2.17995562)<1e-6
    cfft=np.fft.rfft(i)[:51]/n*np.exp(-1j*np.pi*np.arange(51)/n)
    cfft[1:]*=2
    with np.load(DATA/"waveforms.npz") as data:
        c=data["c"]
        assert np.all(c[::2]==0) and np.max(np.abs(c-cfft))<1.e-7
        recon=np.real(np.exp(1j*np.deg2rad(ANGLE)[:,None]*np.arange(51))@c)
        error=np.sqrt(np.mean((recon-data["current"])**2))
        assert error<1.
        shift_error=data["current"][:720]+data["current"][720:1440]
        away=np.all([abs(ANGLE[:720]-pos)>1. for pos in (60,120)],axis=0)
        assert np.max(np.abs(shift_error[away]))<.4
        assert abs(data["current"][np.where(ANGLE==119.75)[0][0]]-12.28)<.1
        assert abs(data["current"][np.where(ANGLE==120.5)[0][0]])<.05
    if study["source"]=="PSCAD":
        assert (DATA/"pscad_record.npz").is_file()
    print(f"Verified two GTOs, four switching edges, 51 Fourier coefficients and source/load powers. Fourier RMS error {error:.3f} A.",flush=True)



def media():
    probe=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-of","json",str(MOVIE)]))
    v,a=probe["streams"]
    assert (v["codec_name"],v["width"],v["height"],a["codec_name"],a["tags"]["language"])==("h264",1920,1080,"aac","eng")
    assert abs(float(v["duration"])-float(a["duration"]))<.08
    cues=json.loads((DATA/"cues.json").read_text())
    assert [c["name"] for c in cues]==["intro","freeze","off","area","energy","phase","spectrum","synthesis","fast","overlay"]
    audio=np.frombuffer(subprocess.check_output(["ffmpeg","-v","error","-i",str(MOVIE),"-vn","-ar","8000","-ac","1","-f","s16le","pipe:1"]),dtype="<i2").astype(float)/32768
    for c in cues:
        clip=audio[round((c["start"]+.1)*8000):round((c["start"]+c["duration"])*8000)]
        assert np.sqrt(np.mean(clip**2))>.012
    a,b=cues[1:3]
    pause=audio[round((a["start"]+a["duration"]+.15)*8000):round((b["start"]-.1)*8000)]
    assert len(pause)>8000 and max(abs(pause))<.01
    subprocess.run(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(MOVIE),"-f","null","-"],check=True)
    print(f"Verified {len(cues)} English narration cues and {float(v['duration']):.2f} s of encoded media.")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--electrical-only",action="store_true")
    opts=ap.parse_args()
    wiring()
    electrical()
    if not opts.electrical_only:
        media()
