"""Run the two project files and validate the native output timestamps."""
from pathlib import Path
import mhi.pscad
import time
import xml.etree.ElementTree as ET
from datetime import datetime

ROOT=Path(__file__).resolve().parent
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--port',type=int)
port=parser.parse_args().port
app=mhi.pscad.connect(host='127.0.0.1',port=port) if port else mhi.pscad.application()
if not app.licensed():
    raise RuntimeError("A licensed PSCAD session is required.")
workspace=ROOT/'pscad'/'Half_Wave_Rectifier.pswx'
entries=ET.parse(workspace).findall('./projects/project')
if [entry.get('name') for entry in entries]!=['DirectResistor','HalfWaveDiode']:
    raise RuntimeError('Unexpected project list in the rectifier workspace.')
app.load(str(workspace))
for entry in entries:
    name=entry.attrib['name']
    path=workspace.parent/entry.attrib['filepath']
    proj=app.project(name)
    if Path(proj.filename).resolve()!=path.resolve():
        raise RuntimeError(f'A different {name} is already open.')
    start=time.time()
    proj.run()
    msgs=list(proj.messages())
    for msg in msgs: print(msg.status,msg.text,flush=True)
    if any('error' in str(m.status).lower() or 'fatal' in str(m.status).lower() for m in msgs):
        raise RuntimeError(f'{name}: PSCAD reported errors.')
    outputs=[p for p in path.parent.glob(name+'.*/'+name+'_01.out') if p.stat().st_mtime>=start-2 and p.stat().st_size>1000]
    if len(outputs)!=1:raise RuntimeError(f'{name}: fresh output missing')
    print(datetime.now(),outputs[0],flush=True)


