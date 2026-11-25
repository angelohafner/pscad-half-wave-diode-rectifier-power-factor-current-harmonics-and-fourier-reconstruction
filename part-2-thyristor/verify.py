"""Cross-check the reference, acquisition mode, media and dedicated workspace."""
from pathlib import Path
import hashlib
import json
import subprocess
import wave
import xml.etree.ElementTree as ET
import numpy as np
from analyze import ROOT,ideal_coeff,IP

s=json.loads((ROOT/'data/study.json').read_text())
m=s['scr']; ref=ideal_coeff(90)
n=262144
theta=(np.arange(n)+.5)*2*np.pi/n
i=np.where((theta>=np.pi/2)&(theta<np.pi),IP*np.sin(theta),0)
co=np.fft.rfft(i)/n
co[:51]*=np.exp(-1j*np.pi*np.arange(51)/n)
co[1:51]*=2
assert max(abs(co[:51]-ref))<3.e-8
assert abs(np.mean(i*120*np.sqrt(2)*np.sin(theta))-300)<1.e-5
assert abs(np.sqrt(np.mean(i*i))-5)<1.e-6
assert abs(m['disp']*m['df']-m['pf'])<5.e-4
assert abs(m['q']-600/np.pi)<2 and abs(m['phase']-np.rad2deg(np.arctan(2/np.pi)))<.3
if s['native']:assert (ROOT/'data/pscad_samples.npz').is_file()
w=ET.parse(ROOT/'pscad/Part2_Thyristor_90deg.pswx')
projects=w.findall('./projects/project')
assert len(projects)==1 and projects[0].get('name')=='HalfWaveSCR90'
case=ET.parse(ROOT/'pscad'/projects[0].get('filepath').replace('\\','/'))
switch=case.find(".//User[@defn='master:peswitch']")
assert switch.find("./paramlist/param[@name='Type']").get('value')=='1'
assert case.find(".//User[@defn='HalfWaveSCR90:PeakGate']") is not None
p=ROOT/'Thyristor_90deg_Power_Factor_and_Gibbs.mp4'
info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(p)]))
v,a=info['streams']
assert (v['width'],v['height'],a['tags'].get('language'))==(1920,1080,'eng')
assert abs(float(v['duration'])-float(a['duration']))<.08
cues=json.loads((ROOT/'data/cues.json').read_text())
assert [c['name'] for c in cues]==['intro','freeze','fire','phase','power','box','spectrum','slow','fast','overlay','gibbs']
audio=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-vn','-ar','8000','-ac','1','-f','s16le','pipe:1']),dtype='<i2').astype(float)/32768
for cue in cues:
    t,d=cue['start'],cue['duration']
    clip=audio[round((t+.1)*8000):round((t+d)*8000)]
    assert np.sqrt(np.mean(clip**2))>.014, cue['name']
pause=audio[round((cues[1]['start']+cues[1]['duration']+.16)*8000):round((cues[2]['start']-.12)*8000)]
assert len(pause)>8000 and max(abs(pause))<.005
subprocess.run(['ffmpeg','-nostdin','-v','error','-xerror','-i',str(p),'-f','null','-'],check=True)
print('Validated',round(float(v['duration']),2),'s;',len(cues),'voice cues; native recording:',s['native'])
print('Video SHA256:',hashlib.sha256(p.read_bytes()).hexdigest())
