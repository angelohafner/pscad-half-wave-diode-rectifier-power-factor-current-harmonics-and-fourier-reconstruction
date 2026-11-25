"""Render with Manim and align narration to encoded frame boundaries."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from manim import config
from pydub import AudioSegment
from film import ROOT, ThyristorFilm

def frame_count(path):
    out=subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames','-of','csv=p=0',str(path)])
    return int(out.strip())

if __name__=='__main__':
    with tempfile.TemporaryDirectory(prefix='scr90_film_') as tmp:
        original=Path.cwd()
        try:
            os.chdir(tmp)
            config.media_dir='render'
            config.input_file=str(ROOT/'film.py')
            config.output_file='Thyristor_90deg'
            config.pixel_width=1920
            config.pixel_height=1080
            config.frame_rate=24
            config.max_files_cached=-1
            config.progress_bar='none'
            config.verbosity='WARNING'
            scene=ThyristorFilm()
            scene.render()
            writer=scene.renderer.file_writer
            counts={}
            start=[0]
            for partial in writer.partial_movie_files:
                if partial not in counts:counts[partial]=frame_count(partial)
                start.append(start[-1]+counts[partial])
            total=frame_count(writer.movie_file_path)
            assert total==start[-1],(total,start[-1])
            track=AudioSegment.silent(duration=round(1000*total/24),frame_rate=48000).set_sample_width(2)
            cues=[]
            for name,idx,duration in scene.cues:
                when=start[idx]/24+.10
                clip=AudioSegment.from_wav(ROOT/'media'/'voice'/(name+'.wav')).set_frame_rate(48000)
                assert when+duration<=total/24+.03,(name,when,duration,total)
                if cues:assert when>=cues[-1]['start']+cues[-1]['duration']-.05
                track=track.overlay(clip,position=round(when*1000))
                cues.append(dict(name=name,start=when,duration=duration))
            track.export('voice.wav',format='wav')
            target=ROOT/'Thyristor_90deg_Power_Factor_and_Gibbs.mp4'
            staged=ROOT/'media'/'new_film.mp4'
            subprocess.run(['ffmpeg','-nostdin','-y','-v','error','-i',str(writer.movie_file_path),'-i','voice.wav',
                            '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','144k',
                            '-metadata:s:a:0','language=eng','-movflags','+faststart',str(staged)],check=True)
            staged.replace(target)
            (ROOT/'data'/'cues.json').write_text(json.dumps(cues,indent=2)+'\n')
            print('Rendered',target.name,'frames',total,'duration',total/24,flush=True)
        finally:
            os.chdir(original)
