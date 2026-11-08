from pathlib import Path
import json,subprocess,time
from PIL import Image
root=Path.cwd(); out=root/'exports/board-previews';out.mkdir(exist_ok=True)
wid=1744444040
script=root/'tmp/pdfs/check-board.js'
reports=[]
for n in range(1,5):
 url=(root/f'board{n}-codex.html').as_uri()
 subprocess.run(['osascript','-e',f'tell application "Google Chrome" to set URL of active tab of window id {wid} to "{url}"'],check=True,capture_output=True)
 time.sleep(.5)
 cmd=f'tell application "Google Chrome" to tell window id {wid} to execute active tab javascript (read POSIX file "{script}" as «class utf8»)'
 for retry in range(10):
  r=subprocess.run(['osascript','-e',cmd],capture_output=True,text=True,check=True)
  report=json.loads(r.stdout)
  if report['fonts']=='loaded' and not report['missingImages']:break
  time.sleep(.3)
 time.sleep(.25)
 raw=root/f'tmp/pdfs/board{n}-window.png'
 subprocess.run(['screencapture','-x','-o','-l3473',str(raw)],check=True)
 with Image.open(raw) as im:
  top=(report['outer'][1]-report['viewport'][1])*2
  crop=im.crop((0,top,1920,top+1440))
  crop.save(out/f'board{n}-codex.png')
 reports.append(report)
 print(json.dumps(report))
(root/'exports/board-validation.json').write_text(json.dumps(reports,indent=2))
