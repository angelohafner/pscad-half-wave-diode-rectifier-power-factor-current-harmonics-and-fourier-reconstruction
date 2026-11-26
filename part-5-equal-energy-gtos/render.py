"""Render the animation and align each English narration clip to its encoded start frame."""
import json
import os
from pathlib import Path
import subprocess
import tempfile

from manim import config
from pydub import AudioSegment
from equal_energy import ROOT, EqualEnergyFilm

MOVIE = "Equal_Energy_GTO_and_SCR.mp4"
FPS = 24


def frame_count(path):
    return int(subprocess.check_output(["ffprobe","-v","error","-select_streams","v:0",
               "-show_entries","stream=nb_frames","-of","csv=p=0",str(path)]).strip())


def render():
    config.media_dir="render"
    config.input_file=str(ROOT/"film.py")
    config.output_file="Equal_Energy"
    config.pixel_width,config.pixel_height,config.frame_rate=1920,1080,FPS
    config.max_files_cached=-1
    config.progress_bar="none"
    config.verbosity="WARNING"
    scene=EqualEnergyFilm()
    scene.render()
    writer=scene.renderer.file_writer
    counts={}
    frames=[0]
    for partial in writer.partial_movie_files:
        if partial not in counts:
            counts[partial]=frame_count(partial)
        frames.append(frames[-1]+counts[partial])
    total=frame_count(writer.movie_file_path)
    assert total==frames[-1]
    audio=AudioSegment.silent(duration=round(total/FPS*1000),frame_rate=48000).set_sample_width(2)
    cues=[]
    for name,index,duration in scene.cues:
        start=frames[index]/FPS+.10
        assert start+duration<=total/FPS and (not cues or start>=cues[-1]["start"]+cues[-1]["duration"])
        clip=AudioSegment.from_wav(ROOT/"media"/"voice"/(name+".wav")).set_frame_rate(48000)
        audio=audio.overlay(clip,position=round(start*1000))
        cues.append(dict(name=name,start=start,duration=duration))
    audio.export("narration.wav",format="wav")
    output=ROOT/"media"/"final.mp4"
    subprocess.run(["ffmpeg","-y","-nostdin","-v","error","-i",str(writer.movie_file_path),"-i","narration.wav",
                    "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","144k",
                    "-metadata:s:a:0","language=eng","-movflags","+faststart",str(output)],check=True)
    output.replace(ROOT/MOVIE)
    (ROOT/"media/cues.json").write_text(json.dumps(cues,indent=2)+"\n",encoding="utf-8")
    print(f"Rendered {total} frames, {total/FPS:.2f} seconds",flush=True)


if __name__=="__main__":
    previous=Path.cwd()
    with tempfile.TemporaryDirectory(prefix="part5_") as folder:
        try:
            os.chdir(folder)
            render()
        finally:
            os.chdir(previous)
