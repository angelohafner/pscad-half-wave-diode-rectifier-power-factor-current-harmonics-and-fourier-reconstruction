"""Align the narration clips with the final encoded animation boundaries."""
import json
from pathlib import Path
import re
import subprocess
import tempfile

import numpy as np
from pydub import AudioSegment

ROOT = Path(__file__).resolve().parents[1]
work = ROOT / 'work'
movie = ROOT / 'Half_Wave_Power_Factor.mp4'
log = (work / 'integral_final.log').read_text(encoding='utf-8-sig')
markers = re.findall(r'Cue (\w+) ([\d.]+) ([\d.]+)', log)
metadata = json.loads(subprocess.check_output([
    'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_packets',
    '-show_entries', 'packet=pts_time,flags:stream=duration', '-of', 'json', str(movie)]))
keyframes = np.sort([float(packet['pts_time']) for packet in metadata['packets'] if 'K' in packet['flags']])
duration = float(metadata['streams'][0]['duration'])
track = AudioSegment.silent(duration=round(duration*1000),frame_rate=48000).set_sample_width(2)
# Each cue starts on a new Manim partial movie. Follow the accumulated frame-rounding offset.
drift = 0.
lines = []
for name, start, length in markers:
    start = float(start)
    boundary = keyframes[np.argmin(np.abs(keyframes-(start+drift)))]
    delta = boundary-start
    if abs(delta-drift)>.21:
        raise ValueError(f'Uncertain animation boundary for {name}: {delta-drift:.3f} s')
    drift = delta
    clip = AudioSegment.from_wav(ROOT/'assets'/'voice'/f'{name}.wav').set_frame_rate(48000)
    track = track.overlay(clip,position=round(1000*(boundary+.12)))
    lines.append(f'Cue {name} {boundary:.6f} {length}')
with tempfile.TemporaryDirectory(prefix='rectifier_narration_') as tmp:
    sound = Path(tmp)/'narration.wav'
    track.export(sound,format='wav')
    replacement = work/'Half_Wave_Power_Factor_mux.mp4'
    subprocess.run(['ffmpeg','-nostdin','-y','-v','error','-i',str(movie),'-i',str(sound),
                    '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','160k',
                    '-ar','48000','-metadata:s:a:0','language=eng','-movflags','+faststart',str(replacement)],check=True)
    replacement.replace(movie)
(work/'integral_audio.log').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Narration attached:',len(lines),'cues |',round(duration,2),'seconds')
