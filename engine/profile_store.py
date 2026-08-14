
import json
from pathlib import Path
from datetime import datetime
ROOT=Path(__file__).resolve().parents[1]
STUDENTS=ROOT/"data"/"students"
STUDENTS.mkdir(parents=True,exist_ok=True)
def load(code):
    p=STUDENTS/(code+".json")
    if p.exists():
        return json.loads(p.read_text())
    now=datetime.now().isoformat()
    data={"code":code,"name":code,"grade":8,"subject":"Mathematics","term":1,"xp":0,"level":1,"streak":0,"mastery":{},"history":[],"created_at":now,"updated_at":now}
    p.write_text(json.dumps(data,indent=2)); return data
def save(data):
    data["updated_at"]=datetime.now().isoformat()
    (STUDENTS/(data["code"]+".json")).write_text(json.dumps(data,indent=2))
