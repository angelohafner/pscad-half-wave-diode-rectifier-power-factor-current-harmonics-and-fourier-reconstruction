"""Check native wiring, independent Fourier integrals, numerical measurements, and encoded media."""
import argparse
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from study import ANGLE, DATA, ROOT, PEAK

NAME="AntiParallelSCR90"
MOVIE=ROOT/"Antiparallel_Thyristors_Same_Power_Factor.mp4"


def param(element, key):
    return element.find(f"./paramlist/param[@name='{key}']").get("value")


def wiring():
    project=ET.parse(ROOT/"pscad/Part3_Antiparallel_90deg.pswx").findall("projects/project")
    assert len(project)==1 and project[0].get("name")==NAME
    case=ET.parse(ROOT/"pscad"/project[0].get("filepath").replace("\\","/"))
    main=case.find(".//Definition[@name='Main']/schematic")
    switches=main.findall("User[@defn='master:peswitch']")
    assert [(param(s,"Name"),s.get("orient"),param(s,"Type"),param(s,"INTR")) for s in switches]==[
        ("SCR1","1","1","0"),("SCR2","3","1","0")]
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
    for e,low,high in [("PeakGate",90,100),("NegativePeakGate",270,280)]:
        code=case.find(f".//Definition[@name='{e}']/script/segment").text
        assert f".GE. {low}.0" in code and f".LT. {high}.0" in code
        assert main.find(f"User[@defn='{NAME}:{e}']") is not None
    assert {param(e,"Name") for e in main.findall("User[@defn='master:pgb']")}>={
        "Gate1","Gate2","Current_A","Voltage_V"}


def electrical():
    study=json.loads((DATA/"results.json").read_text())
    with np.load(DATA/"waveforms.npz") as data:
        c=data["c_pair"]
        assert np.all(c[::2]==0) and np.allclose(c[1::2],2*data["c_single"][1::2])
        # A midpoint-grid quadrature avoids the sample-value ambiguity at either firing instant.
        size=262144
        theta=(np.arange(size)+.5)*2*np.pi/size
        ideal=np.where(theta%np.pi>=np.pi/2,PEAK*np.sin(theta),0.)
        cfft=np.fft.rfft(ideal)[:51]/size*np.exp(-1j*np.pi*np.arange(51)/size)
        cfft[1:]*=2
        assert np.max(np.abs(c-cfft)) < 4e-8
        recon=np.real(np.exp(1j*np.deg2rad(ANGLE)[:,None]*np.arange(51))@c)
        assert np.sqrt(np.mean((recon-data["pair"])**2))<.8
        # Allow finite record resolution at the discontinuity; check the rest of the cycle.
        away_from_firing = np.abs(ANGLE[:720]-90) > 1.0
        symmetry_error = data["pair"][:720]+data["pair"][720:1440]
        assert np.max(np.abs(symmetry_error[away_from_firing]))<.4
    for m in [study["pair"],study["diode"]]:
        assert abs(m["pf"]-1/np.sqrt(2))<.003 and abs(m["ir"]-np.sqrt(50))<.035
        assert abs(m["p"]-600)<2 and abs(m["s"]-120*np.sqrt(50))<3
        assert abs(m["displacement"]*m["distortion"]-m["pf"])<.002
    pair=study["pair"]
    assert abs(pair["dc"])<.02 and abs(pair["lag"]-np.rad2deg(np.arctan(2/np.pi)))<.3
    assert abs(pair["q1"]-1200/np.pi)<3 and abs(study["diode"]["dc"]-PEAK/np.pi)<.02
    print("Verified circuit topology, 51 Fourier coefficients and source-port quantities.",flush=True)


def media():
    probe=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-of","json",str(MOVIE)]))
    v,a=probe["streams"]
    assert (v["codec_name"],v["width"],v["height"],a["codec_name"],a["tags"]["language"])==("h264",1920,1080,"aac","eng")
    assert abs(float(v["duration"])-float(a["duration"]))<.08
    cues=json.loads((DATA/"cues.json").read_text())
    assert [c["name"] for c in cues]==["intro","positive","negative","symmetry","spectrum","synthesis","fast","overlay","power","finish"]
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
