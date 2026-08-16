import json, random, re
from pathlib import Path
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from engine.question_engine import QuestionEngine

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
DATA = Path(App.get_running_app().user_data_dir) if App.get_running_app() else ROOT / "data"

CURRICULUM_FILE = CONTENT / "curriculum" / "grade_map.json"
NOTES_FILE = CONTENT / "notes" / "grade8_notes.json"


def load_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def curriculum():
    return load_json(CURRICULUM_FILE, {"grades": {}})


def notes_pack():
    return load_json(NOTES_FILE, {})


def safe_code(code):
    return "".join(c for c in code.upper() if c.isalnum() or c in "_-" ) or "STUDENT"


class LearnButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(52)
        self.font_size = sp(16)
        self.background_normal = ""
        self.background_color = (0.12, 0.27, 0.45, 1)


class NumericKeyboard(GridLayout):
    def __init__(self, target, **kwargs):
        super().__init__(**kwargs)
        self.cols = 4
        self.spacing = dp(5)
        self.size_hint_y = None
        self.height = dp(190)
        self.target = target
        keys = ["1","2","3","←","4","5","6","C","7","8","9","−","0",".","/","+"]
        for key in keys:
            b = Button(text=key, font_size=sp(18), background_normal="", background_color=(0.18,0.22,0.28,1))
            b.bind(on_release=lambda btn: self.press(btn.text))
            self.add_widget(b)

    def press(self, key):
        if key == "C":
            self.target.text = ""
        elif key == "←":
            self.target.text = self.target.text[:-1]
        else:
            self.target.insert_text(key.replace("−", "-"))


class Base(Screen):
    title = StringProperty("")
    def shell(self, title, body, back=True):
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        header = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
        if back:
            b = LearnButton(text="‹")
            b.size_hint_x = None; b.width = dp(52)
            b.bind(on_release=lambda *_: self.home())
            header.add_widget(b)
        header.add_widget(Label(text=title, font_size=sp(22), bold=True, halign="left", valign="middle"))
        root.add_widget(header)
        root.add_widget(body)
        self.clear_widgets(); self.add_widget(root)

    def home(self): self.manager.current = "home"


class Login(Base):
    def on_pre_enter(self, *args):
        root = BoxLayout(orientation="vertical", padding=dp(24), spacing=dp(12))
        root.add_widget(Widget())
        root.add_widget(Label(text="LEARNLY", font_size=sp(36), bold=True, size_hint_y=None, height=dp(55)))
        root.add_widget(Label(text="Mathematics • Offline • Adaptive", font_size=sp(17), size_hint_y=None, height=dp(35)))
        self.code = TextInput(hint_text="Student code", multiline=False, size_hint_y=None, height=dp(52), font_size=sp(18))
        root.add_widget(self.code)
        self.grade = Spinner(text="Grade 8", values=["Grade R"] + [f"Grade {i}" for i in range(1,10)], size_hint_y=None, height=dp(52), font_size=sp(17))
        root.add_widget(self.grade)
        b = LearnButton(text="START LEARNLY")
        b.bind(on_release=self.login); root.add_widget(b)
        self.status = Label(text="", size_hint_y=None, height=dp(35))
        root.add_widget(self.status); root.add_widget(Widget())
        self.clear_widgets(); self.add_widget(root)

    def login(self, *_):
        if not self.code.text.strip():
            self.status.text = "Enter your student code."
            return
        app = App.get_running_app()
        app.ensure_dirs()
        app.student = app.load_student(safe_code(self.code.text), self.grade.text)
        self.manager.current = "home"


class Home(Base):
    def on_pre_enter(self, *args):
        app = App.get_running_app(); s = app.student
        mastery = sum(s["mastery"].values()) / max(1, len(s["mastery"]))
        body = BoxLayout(orientation="vertical", spacing=dp(8))
        body.add_widget(Label(text=f"Welcome, {s['name']}", font_size=sp(24), bold=True, size_hint_y=None, height=dp(42)))
        body.add_widget(Label(text=f"{s['grade']} Mathematics   •   Level {s['level']}   •   {s['xp']} XP", font_size=sp(15), size_hint_y=None, height=dp(32)))
        p = ProgressBar(max=1, value=mastery, size_hint_y=None, height=dp(12)); body.add_widget(p)
        body.add_widget(Label(text=f"Overall mastery {mastery*100:.0f}%   •   Daily goal {s['today_done']}/{s['daily_goal']}", size_hint_y=None, height=dp(30)))
        actions = [
            ("📚 LEARN — notes, examples & tricks", "learn"),
            ("🎯 PRACTICE — choose a topic", "practice"),
            ("📝 PAPERS — printable worksheets", "papers"),
            ("📊 PROGRESS — mastery & level", "progress"),
            ("⚙ SETTINGS — adjust your learning", "settings"),
        ]
        scroll = ScrollView(); grid = GridLayout(cols=1, spacing=dp(8), size_hint_y=None); grid.bind(minimum_height=grid.setter("height"))
        for text, screen in actions:
            b=LearnButton(text=text); b.bind(on_release=lambda _, n=screen: setattr(self.manager,"current",n)); grid.add_widget(b)
        scroll.add_widget(grid); body.add_widget(scroll)
        self.shell("Learnly", body, back=False)


class Learn(Base):
    def on_pre_enter(self, *args):
        app=App.get_running_app(); grade=app.student["grade"]; data=curriculum(); allowed=data.get("grades",{}).get(grade,{}).get("topics",[])
        body=BoxLayout(orientation="vertical", spacing=dp(8))
        body.add_widget(Label(text=f"Pick a topic • {grade}", font_size=sp(19), bold=True, size_hint_y=None, height=dp(36)))
        scroll=ScrollView(); grid=GridLayout(cols=1, spacing=dp(7), size_hint_y=None); grid.bind(minimum_height=grid.setter("height"))
        for item in allowed:
            tid=item["id"]; mastery=app.student["mastery"].get(tid,0.5)
            b=LearnButton(text=f"{item['name']}   {mastery*100:.0f}%")
            b.bind(on_release=lambda _,t=tid: self.show_topic(t)); grid.add_widget(b)
        scroll.add_widget(grid); body.add_widget(scroll); self.shell("Learn",body)

    def show_topic(self, tid):
        data=notes_pack().get(tid,{})
        body=BoxLayout(orientation="vertical", spacing=dp(7))
        scroll=ScrollView(); box=BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None, padding=dp(4)); box.bind(minimum_height=box.setter("height"))
        box.add_widget(Label(text=data.get("title",tid.replace("_"," ").title()), font_size=sp(23), bold=True, size_hint_y=None, height=dp(45)))
        for key,label in [("note","NOTES"),("tips","TIPS & TRICKS"),("steps","HOW TO DO IT"),("example","WORKED EXAMPLE"),("mistakes","COMMON MISTAKES"),("check","QUICK CHECK")]:
            val=data.get(key)
            if val:
                box.add_widget(Label(text=label,font_size=sp(17),bold=True,size_hint_y=None,height=dp(30)))
                box.add_widget(Label(text=val,font_size=sp(14),text_size=(dp(360),None),size_hint_y=None,height=dp(110)))
        b=LearnButton(text="PRACTICE THIS TOPIC"); b.bind(on_release=lambda *_: self.practice_topic(tid)); box.add_widget(b)
        scroll.add_widget(box); body.add_widget(scroll); self.shell("Topic",body)

    def practice_topic(self,tid):
        App.get_running_app().practice_topic=tid; self.manager.current="practice"


class Practice(Base):
    def on_pre_enter(self,*args):
        app=App.get_running_app(); grade=app.student["grade"]
        body=BoxLayout(orientation="vertical", spacing=dp(7))
        allowed=curriculum().get("grades",{}).get(grade,{}).get("topics",[])
        values=[x["name"] for x in allowed]; self.map={x["name"]:x["id"] for x in allowed}
        self.spinner=Spinner(text=(next((x["name"] for x in allowed if x["id"]==getattr(app,"practice_topic",None)),values[0] if values else "No topic")), values=values, size_hint_y=None,height=dp(50),font_size=sp(16)); body.add_widget(self.spinner)
        self.diff=Spinner(text="Adaptive", values=["Adaptive","Foundation","Standard","Advanced"],size_hint_y=None,height=dp(50)); body.add_widget(self.diff)
        self.question=Label(text="Choose a topic and press START",font_size=sp(19),text_size=(dp(380),None),size_hint_y=None,height=dp(90)); body.add_widget(self.question)
        self.answer=TextInput(hint_text="Answer",multiline=False,size_hint_y=None,height=dp(52),font_size=sp(20)); body.add_widget(self.answer)
        self.keyboard=NumericKeyboard(self.answer); body.add_widget(self.keyboard)
        row=BoxLayout(size_hint_y=None,height=dp(52),spacing=dp(6));
        for text,fn in [("START",self.start),("CHECK",self.check),("HINT",self.hint)]:
            b=LearnButton(text=text); b.bind(on_release=fn); row.add_widget(b)
        body.add_widget(row); self.feedback=Label(text="",text_size=(dp(380),None),size_hint_y=None,height=dp(90)); body.add_widget(self.feedback); self.shell("Practice",body)

    def start(self,*args):
        app=App.get_running_app(); tid=self.map.get(self.spinner.text); self.topic=tid
        allowed=curriculum().get("grades",{}).get(app.student["grade"],{}).get("topic_ids",[])
        if tid not in allowed:
            self.feedback.text="This topic is not enabled for this grade. Learnly will not serve out-of-level maths."
            return
        d={"Foundation":1,"Standard":2,"Advanced":3}.get(self.diff.text,2)
        if self.diff.text=="Adaptive": d=app.recommended_difficulty(tid)
        self.q=QuestionEngine().generate(tid,d); self.question.text=self.q["question"]; self.answer.text=""; self.feedback.text=f"{self.q['topic_name']} • Level {d} • {self.q['marks']} mark(s)"

    def check(self,*args):
        if not hasattr(self,"q"): return
        got=self.answer.text.strip().replace("−","-").replace(" ","").lower(); expected=str(self.q["answer"]).replace(" ","").lower()
        ok=got==expected
        app=App.get_running_app(); old=app.student["mastery"].get(self.topic,0.5); app.student["mastery"][self.topic]=max(0,min(1,old+(0.05 if ok else -0.03))); app.student["today_done"]+=1; app.student["xp"]+=10 if ok else 3; app.student["level"]=1+app.student["xp"]//500; app.save_student()
        self.feedback.text=("✓ Correct\n" if ok else f"✗ Not quite. Answer: {self.q['answer']}\n")+self.q.get("explanation","")

    def hint(self,*args):
        if hasattr(self,"q"): self.feedback.text="💡 "+self.q.get("hint","Think about the rule for this topic.")


class Papers(Base):
    def on_pre_enter(self,*args):
        app=App.get_running_app(); allowed=curriculum().get("grades",{}).get(app.student["grade"],{}).get("topics",[])
        body=BoxLayout(orientation="vertical",spacing=dp(8)); self.topic=Spinner(text="Mixed",values=["Mixed"]+[x["name"] for x in allowed],size_hint_y=None,height=dp(50)); body.add_widget(self.topic)
        self.count=Spinner(text="10",values=["5","10","15","20","30"],size_hint_y=None,height=dp(50)); body.add_widget(self.count)
        b=LearnButton(text="GENERATE PNG PAPER"); b.bind(on_release=self.generate); body.add_widget(b)
        self.out=Label(text="Each paper is rendered locally with Pillow and saved to Learnly/Papers.",text_size=(dp(380),None)); body.add_widget(self.out); self.shell("Paper Generator",body)

    def generate(self,*args):
        app=App.get_running_app(); tid=None
        if self.topic.text!="Mixed":
            for x in curriculum()["grades"][app.student["grade"]]["topics"]:
                if x["name"]==self.topic.text: tid=x["id"]
        from engine.pillow_paper import make_paper
        path=make_paper(app.student,tid,int(self.count.text)); self.out.text=f"✓ Paper created\n{path}\nOpen it from the device Pictures/Learnly folder."


class Progress(Base):
    def on_pre_enter(self,*args):
        s=App.get_running_app().student; body=BoxLayout(orientation="vertical",spacing=dp(7)); scroll=ScrollView(); grid=GridLayout(cols=1,spacing=dp(6),size_hint_y=None); grid.bind(minimum_height=grid.setter("height"))
        for tid,val in sorted(s["mastery"].items(),key=lambda x:x[1]): grid.add_widget(Label(text=f"{tid.replace('_',' ').title()}   {val*100:.0f}%",size_hint_y=None,height=dp(34)))
        scroll.add_widget(grid); body.add_widget(scroll); self.shell("Progress",body)


class Settings(Base):
    def on_pre_enter(self,*args):
        app=App.get_running_app(); s=app.student; body=BoxLayout(orientation="vertical",spacing=dp(8)); body.add_widget(Label(text="Learning adjustments",font_size=sp(20),bold=True,size_hint_y=None,height=dp(40)))
        self.goal=Spinner(text=str(s["daily_goal"]),values=["5","10","20","30","50"],size_hint_y=None,height=dp(50)); body.add_widget(Label(text="Daily goal")); body.add_widget(self.goal)
        self.scale=Spinner(text=s.get("scaling","Adaptive"),values=["Adaptive","Gentle","Standard","Challenge"],size_hint_y=None,height=dp(50)); body.add_widget(Label(text="Question scaling")); body.add_widget(self.scale)
        self.grade=Spinner(text=s["grade"],values=["Grade R"]+[f"Grade {i}" for i in range(1,10)],size_hint_y=None,height=dp(50)); body.add_widget(Label(text="Current grade")); body.add_widget(self.grade)
        b=LearnButton(text="SAVE ADJUSTMENTS"); b.bind(on_release=self.save); body.add_widget(b); self.shell("Settings",body)
    def save(self,*args):
        app=App.get_running_app(); app.student["daily_goal"]=int(self.goal.text); app.student["scaling"]=self.scale.text; app.student["grade"]=self.grade.text; app.student["mastery"]={}; app.sync_curriculum(); app.save_student(); self.manager.current="home"

class LearnlyApp(App):
    def build(self):
        self.student=None; self.practice_topic=None
        sm=ScreenManager(); sm.add_widget(Login(name="login")); sm.add_widget(Home(name="home")); sm.add_widget(Learn(name="learn")); sm.add_widget(Practice(name="practice")); sm.add_widget(Papers(name="papers")); sm.add_widget(Progress(name="progress")); sm.add_widget(Settings(name="settings"));
        self.title="Learnly"; return sm
    def ensure_dirs(self):
        self.data_dir=Path(self.user_data_dir); (self.data_dir/"students").mkdir(parents=True,exist_ok=True); (self.data_dir/"papers").mkdir(parents=True,exist_ok=True)
    def load_student(self,code,grade):
        self.ensure_dirs(); p=self.data_dir/"students"/(code+".json"); defaults={"code":code,"name":f"Student {code}","grade":grade,"daily_goal":20,"today_done":0,"xp":0,"level":1,"scaling":"Adaptive","mastery":{}}
        s=defaults
        if p.exists():
            try:s.update(json.loads(p.read_text(encoding="utf-8")))
            except Exception: pass
        s["grade"]=grade; self.student=s; self.sync_curriculum(); self.save_student(); return s
    def sync_curriculum(self):
        grade=self.student["grade"]; topics=curriculum().get("grades",{}).get(grade,{}).get("topic_ids",[]); m=self.student.setdefault("mastery",{}); 
        for t in topics:m.setdefault(t,0.5)
        self.student["mastery"]={k:v for k,v in m.items() if k in topics}
    def save_student(self):
        if not self.student:return
        self.ensure_dirs(); p=self.data_dir/"students"/(safe_code(self.student["code"])+".json"); p.write_text(json.dumps(self.student,indent=2,ensure_ascii=False),encoding="utf-8")
    def recommended_difficulty(self,tid):
        v=self.student.get("mastery",{}).get(tid,0.5)
        return 1 if v<0.4 else 2 if v<0.7 else 3 if v<0.9 else 4

if __name__ == "__main__": LearnlyApp().run()
