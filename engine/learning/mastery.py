class MasteryEngine:
    def __init__(self,student): self.student=student; self.mastery=student.setdefault('mastery',{})
    def score(self,topic,correct,difficulty=1):
        old=float(self.mastery.get(topic,.5)); step=.04+min(.04,difficulty*.01)
        self.mastery[topic]=max(0,min(1,round(old+(step if correct else -step*1.25),4)))
        self.refresh(); return self.mastery[topic]
    def refresh(self):
        items=sorted(self.mastery.items(),key=lambda x:x[1]); self.student['weaknesses']=[k for k,v in items if v<.65][:5]; self.student['strengths']=[k for k,v in reversed(items) if v>=.8][:5]
