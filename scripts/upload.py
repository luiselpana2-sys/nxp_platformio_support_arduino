import os,sys,glob,subprocess
from pathlib import Path
if len(sys.argv)<3: raise SystemExit('Usage: upload.py firmware.elf LINKSERVER_TARGET')
elf=os.path.abspath(sys.argv[1]); target=sys.argv[2]
paths=[]
for base in (r'C:\NXP',os.environ.get('NXP_LINKSERVER_DIR','')):
 if base and os.path.isdir(base):
  paths.extend(glob.glob(os.path.join(base,'LinkServer*','LinkServer.exe')))
  paths.extend(glob.glob(os.path.join(base,'LinkServer.exe')))
exe=os.environ.get('LINKSERVER_EXE') or (sorted(paths,reverse=True)[0] if paths else None)
if not exe: raise SystemExit('LinkServer.exe not found. Set LINKSERVER_EXE to its full path.')
args=[exe,'flash']
probe=os.environ.get('LINKSERVER_PROBE')
if probe: args+=['--probe',probe]
args += [target,'load',elf]
print('Running:',args)
sys.exit(subprocess.call(args))
