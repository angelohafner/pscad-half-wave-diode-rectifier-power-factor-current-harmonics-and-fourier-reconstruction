from pathlib import Path
import sys
import os
import tempfile
import shutil
from manim import config

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from film import RectifierFilm
# Manim requires a canonical directory handle for its intermediate movie files.
# Use the process-local temporary directory, then copy the completed MP4 once.
media=Path(tempfile.mkdtemp(prefix="halfwave_media_"))
cached=os.environ.get('HALFWAVE_RENDER_CACHE')
if cached:
    shutil.copytree(Path(cached),media/'render')
print("Render directory:",media,flush=True)
os.chdir(media)
config.media_dir='render'
config.input_file=str(root/'film.py')
config.output_file='Half_Wave_Power_Factor'
config.pixel_width=1920
config.pixel_height=1080
config.frame_rate=24
config.max_files_cached=-1
config.progress_bar="none"
config.verbosity="WARNING"
scene=RectifierFilm()
scene.render()
shutil.copy2(scene.renderer.file_writer.movie_file_path,root/'Half_Wave_Power_Factor.mp4')

