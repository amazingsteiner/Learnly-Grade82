from datetime import datetime
class SessionEngine:
    def __init__(self,student): self.student=student; self.history=student.setdefault("history",[])
    def record(self,q,user,correct):
        e={"question_id":q["id"],"topic":q["topic"],"difficulty":q["difficulty"],
           "answer":str(user),"correct":bool(correct),"timestamp":datetime.now().isoformat()}
        self.history.append(e); self.student["today_done"]=self.student.get("today_done",0)+1
        if correct: self.student["xp"]=self.student.get("xp",0)+10
        self.student["updated_at"]=datetime.now().isoformat(); return e
