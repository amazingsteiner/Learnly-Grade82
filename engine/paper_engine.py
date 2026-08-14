import json
from datetime import datetime
from pathlib import Path
from engine.question_engine import QuestionEngine
from engine.learning.adaptive import AdaptiveEngine
class PaperEngine:
    def __init__(self,root): self.root=Path(root); self.q=QuestionEngine()
    def generate(self,student,mode="recommended",count=20,term=None):
        a=AdaptiveEngine(student); qs=[]
        for i in range(count):
            topic=a.choose_topic("weakness" if mode=="weakness" else "strength" if mode=="strength" else "recommended")
            qs.append(self.q.generate(topic,1+(i%3)//2))
        p={"id":"P"+datetime.now().strftime("%Y%m%d%H%M%S"),"student_code":student["code"],
           "term":term if term is not None else student.get("term",3),"mode":mode,
           "created_at":datetime.now().isoformat(),"questions":qs}
        path=self.root/"data"/"papers"/f"{p['id']}.json"; path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(p,indent=2,ensure_ascii=False),encoding="utf-8")
        student.setdefault("papers",[]).append({"id":p["id"],"mode":mode,"term":p["term"],"created_at":p["created_at"]})
        return p,path
