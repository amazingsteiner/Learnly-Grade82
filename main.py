
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, NumericProperty
from kivy.clock import Clock
from pathlib import Path
import json, random, sys

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from engine.question_engine import QuestionEngine, TOPICS
from engine.profile_store import load, save
from engine.adaptive import recommendation

class LoginScreen(Screen):
    def login(self):
        code=self.ids.code.text.strip() or "S01"
        app=App.get_running_app()
        app.student=load(code)
        self.manager.current="home"

class HomeScreen(Screen):
    def on_pre_enter(self,*a):
        s=App.get_running_app().student
        self.ids.welcome.text=f"Welcome, {s.get('name',s['code'])}"
        self.ids.stats.text=f"Grade 8 Mathematics  •  XP {s.get('xp',0)}  •  Streak {s.get('streak',0)}"

class LearnScreen(Screen):
    def on_pre_enter(self,*a):
        self.ids.topic_spinner.values=TOPICS
        self.show_topic(TOPICS[0])
    def show_topic(self,topic):
        path=ROOT/"content"/"grade8"/"topics"/(topic.lower().replace(" & ","_").replace(" ","_")+".json")
        try: d=json.loads(path.read_text())
        except: d={"title":topic,"what":"Topic module","why":"","key_vocabulary":[],"steps":[]}
        self.ids.note.text=(f"[b]{d['title']}[/b]\n\n"
            f"[b]What is it?[/b]\n{d.get('what','')}\n\n"
            f"[b]Why it matters[/b]\n{d.get('why','')}\n\n"
            f"[b]Key vocabulary[/b]\n{', '.join(d.get('key_vocabulary',[]))}\n\n"
            f"[b]Step-by-step[/b]\n"+"\n".join(f"{i+1}. {x}" for i,x in enumerate(d.get("steps",[])))+
            f"\n\n[b]Worked example[/b]\n{d.get('worked_example','')}\n\n"
            f"[b]Common mistakes[/b]\n"+"\n".join("• "+x for x in d.get("common_mistakes",[]))+
            f"\n\n[b]Memory trick[/b]\n{d.get('memory_trick','')}")
    def changed(self,topic): self.show_topic(topic)

class PracticeScreen(Screen):
    question=None
    count=0
    score=0
    def on_pre_enter(self,*a):
        self.ids.topic.values=TOPICS
    def start(self):
        self.count=0; self.score=0; self.next_question()
    def next_question(self):
        topic=self.ids.topic.text if self.ids.topic.text in TOPICS else None
        diff={"Foundation":1,"Standard":2,"Advanced":3,"Elite":4}.get(self.ids.diff.text,1)
        self.question=QuestionEngine().generate(topic,diff)
        self.ids.question.text=self.question["question"]
        self.ids.answer.text=""
        self.ids.feedback.text=f"Question {self.count+1}  •  {self.question['topic']}"
        self.ids.hint.text=""
    def submit(self):
        if not self.question: self.start(); return
        given=self.ids.answer.text.strip()
        correct=given.lower()==self.question["answer"].lower()
        self.count+=1
        if correct:
            self.score+=1
            self.ids.feedback.text=f"✓ Correct! Score {self.score}/{self.count}"
        else:
            self.ids.feedback.text=f"✗ Not quite. Answer: {self.question['answer']}"
        self.ids.hint.text=self.question["explanation"]
        s=App.get_running_app().student
        t=self.question["topic"]; m=s.setdefault("mastery",{}).get(t,50)
        s["mastery"][t]=max(0,min(100,m+(6 if correct else -4)))
        s["xp"]=s.get("xp",0)+(10 if correct else 2)
        s.setdefault("history",[]).append({"topic":t,"correct":correct})
        save(s)
    def hint(self): 
        if self.question: self.ids.hint.text="Hint: "+self.question["hint"]

class PapersScreen(Screen):
    def generate(self):
        topic=self.ids.topic.text if self.ids.topic.text in TOPICS else None
        qe=QuestionEngine(); qs=[qe.generate(topic,2) for _ in range(int(self.ids.num.text or 5))]
        self.ids.paper.text="\n\n".join(f"{i+1}. {q['question']}   [{q['marks']} mark(s)]" for i,q in enumerate(qs))
        self._questions=qs
    def memo(self):
        if hasattr(self,"_questions"):
            self.ids.paper.text="\n\n".join(f"{i+1}. {q['answer']}\nWorking: {q['explanation']}" for i,q in enumerate(self._questions))

class LabScreen(Screen):
    def calculate(self):
        raw=self.ids.values.text.replace(","," ").split()
        try:
            vals=[float(x) for x in raw]; vals.sort()
            n=len(vals); mean=sum(vals)/n
            med=vals[n//2] if n%2 else (vals[n//2-1]+vals[n//2])/2
            freq={x:vals.count(x) for x in vals}; mode=max(freq,key=freq.get)
            self.ids.result.text=f"Count: {n}\nMean: {mean:g}\nMedian: {med:g}\nMode: {mode:g}\nRange: {max(vals)-min(vals):g}"
        except Exception: self.ids.result.text="Enter numbers separated by spaces."

class LearnlyApp(App):
    student={}
    def build(self):
        return Builder.load_file(str(ROOT/"learnly.kv"))

if __name__=="__main__":
    LearnlyApp().run()
