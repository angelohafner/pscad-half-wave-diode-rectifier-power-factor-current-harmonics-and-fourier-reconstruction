"""Check the revised film, recorded power values, and deliberate answer pauses."""
import io
import json
from pathlib import Path
import re
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from prepare import analyze, native_record

def run(*args):
    return subprocess.check_output(list(args))

video = str(ROOT / 'Half_Wave_Power_Factor.mp4')
meta = json.loads(run('ffprobe','-v','error','-show_streams','-show_format','-of','json',video))
vid = next(s for s in meta['streams'] if s['codec_type']=='video')
aud = next(s for s in meta['streams'] if s['codec_type']=='audio')
duration = float(vid['duration'])
print('Video:', vid['codec_name'], vid['width'], vid['height'], duration, vid['nb_frames'], flush=True)
print('Audio:', aud['codec_name'], aud['sample_rate'], aud['duration'], flush=True)
assert (vid['width'],vid['height'])==(1920,1080)
assert abs(duration-float(aud['duration']))<3.1
buf=run('ffmpeg','-nostdin','-v','error','-i',video,'-map','0:a:0','-ac','1','-ar','16000','-f','s16le','pipe:1')
audio=np.frombuffer(buf,dtype='<i2').astype(float)/32768
log=(ROOT/'work'/'integral_audio.log').read_text(encoding='utf-8-sig')
cues={key:(float(t),float(length)) for key,t,length in re.findall(r'Cue (\w+) ([\d.]+) ([\d.]+)',log)}
order='intro waves inst rms power pf spectrum phase product_intro product0 result0 product1 result1 product2 result2 product4 result4 triangle box face distortion slow fast end rules'.split()
assert list(cues)==order, list(cues)
def rms(t0,t1):
    samples=audio[round(t0*16000):round(t1*16000)]
    return np.sqrt(np.mean(samples*samples))
for key,(start,length) in cues.items():
    assert rms(start+.2,start+length)>.015, key
# Compare the delivered soundtrack with the newly synthesized voice at each cue.
from scipy.signal import correlate
for key,(start,length) in cues.items():
    reference=run('ffmpeg','-nostdin','-v','error','-i',str(ROOT/'assets'/'voice'/(key+'.wav')),
                  '-ac','1','-ar','16000','-f','s16le','pipe:1')
    sample=np.frombuffer(reference,dtype='<i2').astype(float)[3200:35200]/32768
    lo=round((start+.02)*16000)
    hi=round((start+.7)*16000)+len(sample)
    window=audio[lo:hi]
    match=correlate(window,sample,mode='valid',method='fft')
    shift=int(np.argmax(match))
    corr=match[shift]/(np.linalg.norm(sample)*np.linalg.norm(window[shift:shift+len(sample)]))
    assert corr>.93, (key,corr)
for q,a in [('power','pf')]+[(f'product{h}',f'result{h}') for h in (0,1,2,4)]:
    start=sum(cues[q])+.22
    stop=cues[a][0]-.1
    assert stop-start>1.25 and rms(start,stop)<.002, (q,stop-start,rms(start,stop))
print('All 25 spoken segments and five answer pauses checked.', flush=True)
data=json.loads((ROOT/'assets'/'data.json').read_text())
for key,case in [('direct','DirectResistor'),('diode','HalfWaveDiode')]:
    measured=analyze(*native_record(case))
    for prop in ['p','s','pf','vr','ir','i1','q1','residual_va','err']:
        assert np.isclose(measured[prop],data[key][prop],atol=1.e-8), (key,prop)
    for h in ['0','1','2','4']:
        for prop in ['mean','positive_j','negative_j']:
            assert np.isclose(measured['products'][h][prop], data[key]['products'][h][prop], atol=1.e-8)
    print(case, {k:round(measured[k],6) for k in ['p','s','pf','q1','err']},flush=True)
for h,totals in data['diode']['products'].items():
    assert np.isclose(60*(totals['positive_j']+totals['negative_j']),totals['mean'],atol=1.e-8)
    print('Order',h,'signed joules per cycle:',round(totals['positive_j'],4),round(totals['negative_j'],4),flush=True)
source=(ROOT/'film.py').read_text(encoding='utf-8')
spoken=(ROOT/'voice.ps1').read_text(encoding='utf-8')
assert all(token not in source for token in [r'\langle',r'\rangle','prms','RMS of product'])
assert all(token not in spoken for token in ['R M S value of instantaneous power','watts R M S','R M S value of about'])
assert r'\int_0^T' in source and 'enUS_DavidM' in spoken
assert 1.8<duration-sum(cues['rules'])<3.2
targets=[('rms',5),('pf',5),('result0',2),('result1',2),('result2',2),('result4',2),
         ('triangle',2),('box',5),('face',6),('fast',5),('end',4),('rules',10)]
sheet=Image.new('RGB',(1120,6*335),'#1a2530')
for k,(key,offset) in enumerate(targets):
    t=cues[key][0]+offset
    data=run('ffmpeg','-nostdin','-v','error','-ss',str(t),'-i',video,'-vframes','1','-vf','scale=560:-1','-f','image2pipe','-c:v','mjpeg','pipe:1')
    x=(k%2)*560;y=(k//2)*335
    sheet.paste(Image.open(io.BytesIO(data)),(x,y)); ImageDraw.Draw(sheet).text((x+6,y+316),key,fill='white')
sheet.save(ROOT/'work'/'integral_check.jpg',quality=93)
subprocess.run(['ffmpeg','-nostdin','-v','error','-xerror','-i',video,'-f','null','-'],check=True)
print('Full decode and visual check frames ready.',flush=True)
