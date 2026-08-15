
import os, sys, json, random
from pathlib import Path
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window

from engine.question_engine import QuestionEngine
from engine.paper_engine import PaperEngine
from engine.adaptive import AdaptiveEngine
from engine.mastery import MasteryEngine
from engine.answer_check import answers_match
from engine.content_loader import all_topics, load_topic_notes, topic_name, content_status
from engine.quiz_engine import DefinitionsQuizEngine

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
STUDENTS = DATA / "students"
PAPERS = DATA / "papers"
EXPORTS = DATA / "exports"
for d in (DATA, STUDENTS, PAPERS, EXPORTS): d.mkdir(parents=True, exist_ok=True)

DEV_MODE = True
DEV_CODE = "DEV-2026"
ACCESS_CODE = "children of the sun"

# Offline V1 economy. All values are configuration, not payment processing.
ECONOMY = {
    "paper": 400,
    "weakness_paper": 400,
    "diagnostic": 250,
    "weakness_drill": 300,
    "packs": {
        "Starter": {"price": 19.99, "credits": 2000},
        "Exam Prep": {"price": 49.99, "credits": 6000},
        "Ultimate": {"price": 99.99, "credits": 15000},
        "Mega": {"price": 199.99, "credits": 30000},
    }
}

def create_default_student(code):
    now=datetime.now().isoformat()
    return {
        "code": code, "name": f"Student {code}", "grade": 8, "subject":"Mathematics", "term":1,
        "daily_goal":20, "today_done":0, "daily_goal_date":datetime.now().strftime("%Y-%m-%d"),
        "streak":0, "xp":0, "level":1, "created_at":now, "updated_at":now, "last_login":now,
        "mastery":{t:0.5 for t in QuestionEngine.TOPICS}, "topic_stats":{},
        "history":[], "papers":[], "mistakes":[], "strengths":[], "weaknesses":[],
        "mental_best_streak":0, "credits":0, "credit_transactions":[], "dev_mode":False,
        "schema_version":3
    }

def save_student(app):
    if not app.student or not app.student_path: return
    app.student["updated_at"]=datetime.now().isoformat()
    app.student_path.write_text(json.dumps(app.student,indent=2,ensure_ascii=False),encoding="utf-8")

def add_tx(app, kind, amount, meta=None):
    s=app.student
    before=int(s.get("credits",0)); after=max(0,before+int(amount)); s["credits"]=after
    s.setdefault("credit_transactions",[]).append({
        "id":"TX-"+datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "type":kind,"credits":int(amount),"balance_before":before,"balance_after":after,
        "timestamp":datetime.now().isoformat(),"environment":"development" if s.get("dev_mode") else "offline",
        **(meta or {})
    })
    save_student(app)

def title(text,size=24):
    return Label(text=text,font_size=dp(size),bold=True,size_hint_y=None,height=dp(size+18))
def body(text,size=15):
    return Label(text=text,font_size=dp(size),halign="left",valign="top",text_size=(None,None),size_hint_y=None)
def btn(text, callback, h=52):
    b=Button(text=text,size_hint_y=None,height=dp(h),font_size=dp(15))
    b.bind(on_release=callback); return b
def card_box():
    b=BoxLayout(orientation="vertical",padding=dp(14),spacing=dp(9),size_hint_y=None)
    b.bind(minimum_height=b.setter("height"))
    with b.canvas.before:
        Color(.97,.98,1,1); b.rect=RoundedRectangle(pos=b.pos,size=b.size,radius=[dp(14)])
    b.bind(pos=lambda *_: setattr(b.rect,"pos",b.pos),size=lambda *_: setattr(b.rect,"size",b.size))
    return b

class BaseScreen(Screen):
    def __init__(self, **kw): super().__init__(**kw); self.content=BoxLayout(orientation="vertical",spacing=dp(8),padding=dp(10)); self.add_widget(self.content)
    def header(self, text, back=True):
        row=BoxLayout(size_hint_y=None,height=dp(58),spacing=dp(8))
        if back: row.add_widget(btn("‹ Back",lambda *_: self.app.go("home"),48))
        row.add_widget(title(text,22)); self.content.add_widget(row)
    @property
    def app(self): return App.get_running_app()
    def scroll(self):
        sv=ScrollView(); box=BoxLayout(orientation="vertical",spacing=dp(10),padding=dp(4),size_hint_y=None); box.bind(minimum_height=box.setter("height")); sv.add_widget(box); self.content.add_widget(sv); return box

class LoginScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        outer=BoxLayout(orientation="vertical",padding=dp(25),spacing=dp(14))
        outer.add_widget(Label(text="LEARNLY",font_size=dp(38),bold=True,size_hint_y=None,height=dp(65)))
        outer.add_widget(Label(text="Grade 8 • Offline Mathematics",font_size=dp(18),size_hint_y=None,height=dp(40)))
        outer.add_widget(Label(text="Adaptive learning that works without data.",font_size=dp(14),size_hint_y=None,height=dp(40)))
        self.code=TextInput(hint_text="Student code",multiline=False,size_hint_y=None,height=dp(54),font_size=dp(17))
        outer.add_widget(self.code)
        outer.add_widget(btn("ENTER LEARNLY",self.login,58))
        outer.add_widget(Label(text="Your progress is stored locally on this device.",font_size=dp(12)))
        self.add_widget(outer)
    def login(self,*_):
        code=self.code.text.strip().upper()
        if not code: return
        STUDENTS.mkdir(parents=True,exist_ok=True); path=STUDENTS/(code+".json")
        if path.exists():
            try: student=json.loads(path.read_text(encoding="utf-8"))
            except Exception: student=create_default_student(code)
        else: student=create_default_student(code)
        defaults=create_default_student(code)
        for k,v in defaults.items(): student.setdefault(k,v)
        for t in QuestionEngine.TOPICS: student.setdefault("mastery",{}).setdefault(t,.5)
        student["grade"]=8; student["last_login"]=datetime.now().isoformat()
        today=datetime.now().strftime("%Y-%m-%d")
        if student.get("daily_goal_date")!=today: student["daily_goal_date"]=today; student["today_done"]=0
        self.app.student=student; self.app.student_path=path; save_student(self.app)
        self.app.go("home")

class HomeScreen(BaseScreen):
    def on_pre_enter(self):
        self.content.clear_widgets(); self.header("Learnly")
        s=self.app.student
        wallet=card_box()
        wallet.add_widget(Label(text=f"🪙 {s.get('credits',0):,} CREDITS",font_size=dp(24),bold=True,size_hint_y=None,height=dp(44)))
        wallet.add_widget(Label(text=f"Level {s.get('level',1)} • {s.get('xp',0):,} XP • 🔥 {s.get('streak',0)} day streak",font_size=dp(14),size_hint_y=None,height=dp(28)))
        wallet.add_widget(Label(text=f"Mastery: {round(self.app.mastery.overall()*100)}%",font_size=dp(14),size_hint_y=None,height=dp(28)))
        self.content.add_widget(wallet)
        grid=GridLayout(cols=2,spacing=dp(8),size_hint_y=None)
        actions=[("📚 Learn","learn"),("✍ Practice","practice"),("📄 Papers","papers"),("🎯 Weakness","weakness"),("🧠 Definitions Quiz","quiz"),("👤 Profile","profile"),("⚙ Settings","settings")]
        if s.get("dev_mode") and DEV_MODE: actions.append(("🔧 DEV Store","dev"))
        for label,name in actions: grid.add_widget(btn(label,lambda _,n=name:self.app.go(n),58))
        grid.bind(minimum_height=grid.setter("height")); self.content.add_widget(grid)
        if DEV_MODE and not s.get("dev_mode"):
            self.content.add_widget(btn("Developer Mode",lambda *_: self.app.go("dev_gate"),48))

class LearnScreen(BaseScreen):
    def on_pre_enter(self):
        self.content.clear_widgets(); self.header("Learn")
        box=self.scroll()
        for t in all_topics():
            tid=t["id"]; name=t["name"]; m=self.app.student["mastery"].get(tid,.5)
            b=btn(f"{t.get('icon','📘')} {name}  •  {round(m*100)}%",lambda _,x=tid:self.open_topic(x),56)
            box.add_widget(b)
    def open_topic(self,tid): self.app.topic_id=tid; self.app.go("topic")

class TopicScreen(BaseScreen):
    def on_pre_enter(self):
        self.content.clear_widgets(); self.header(topic_name(self.app.topic_id)); box=self.scroll()
        d=load_topic_notes(self.app.topic_id) or {}
        sections=[("What is it?",d.get("what_is_it","")),("Why it matters",d.get("why_it_matters","")),("Core concept",d.get("core_concept","")),("Rules",d.get("rules","")),("Formulae",d.get("formulae","")),("Step-by-step",d.get("step_by_step_method","")),("Worked example",str(d.get("worked_example_1",""))),("Common mistakes",d.get("common_mistakes","")),("Memory trick",d.get("memory_trick",""))]
        for h,t in sections:
            if t:
                box.add_widget(title(h,19)); l=body(str(t),14); l.text_size=(dp(390),None); l.height=dp(max(55, len(str(t))/45*22+30)); box.add_widget(l)
        box.add_widget(btn("Practice this topic",lambda *_: self.start(),54))
    def start(self): self.app.practice_topics=[self.app.topic_id]; self.app.go("practice")

class PracticeScreen(BaseScreen):
    def on_pre_enter(self):
        self.content.clear_widgets(); self.header("Practice")
        box=self.scroll()
        box.add_widget(Label(text="Choose a mode",font_size=dp(18),bold=True,size_hint_y=None,height=dp(35)))
        modes=[("Recommended","recommended"),("Weakness Recovery","weakness"),("Strength Challenge","strength"),("Mixed","mixed")]
        for label,mode in modes: box.add_widget(btn(label,lambda _,m=mode:self.start(m),54))
        box.add_widget(title("Question count",18))
        self.count=Spinner(text="10",values=["5","10","15","20"],size_hint_y=None,height=dp(50)); box.add_widget(self.count)
        self.diff=Spinner(text="Standard",values=["Foundation","Standard","Advanced","Elite"],size_hint_y=None,height=dp(50)); box.add_widget(self.diff)
    def start(self,mode):
        self.app.practice_mode=mode; self.app.practice_count=int(self.count.text); self.app.practice_diff=self.diff.text
        self.app.go("session")

class SessionScreen(BaseScreen):
    def on_pre_enter(self):
        self.content.clear_widgets(); self.header("Practice Session")
        self.qe=QuestionEngine(); self.index=0; self.correct=0; self.questions=[]; self.started=datetime.now()
        mode=self.app.practice_mode; topics=self.app.practice_topics or []
        ad=AdaptiveEngine(self.app.student)
        if not topics:
            topics=ad.choose_topics("weakness" if mode=="weakness" else "strength" if mode=="strength" else "mixed", self.app.practice_count)
        for i in range(self.app.practice_count):
            topic=topics[i%len(topics)] if topics else random.choice(QuestionEngine.TOPICS)
            diff=ad.recommend_difficulty(topic) if mode=="recommended" else {"Foundation":1,"Standard":2,"Advanced":3,"Elite":4}.get(self.app.practice_diff,2)
            self.questions.append(self.qe.generate(topic,diff))
        self.show_q()
    def show_q(self):
        self.content.clear_widgets(); self.header(f"Question {self.index+1}/{len(self.questions)}",False)
        q=self.questions[self.index]
        box=self.scroll()
        box.add_widget(Label(text=f"{q['topic_name']} • Difficulty {q['difficulty']} • {q['marks']} mark(s)",font_size=dp(14),size_hint_y=None,height=dp(35)))
        l=body(q["question"],19); l.text_size=(dp(390),None); l.height=dp(max(90,len(q["question"])/42*30+50)); box.add_widget(l)
        if q.get("hint") and self.app.student.get("settings",{}).get("hints",True):
            box.add_widget(Label(text="Hint: "+q["hint"],font_size=dp(13),size_hint_y=None,height=dp(55)))
        self.answer=TextInput(hint_text="Your answer",multiline=False,size_hint_y=None,height=dp(54),font_size=dp(17)); box.add_widget(self.answer)
        box.add_widget(btn("CHECK ANSWER",self.check,54))
        self.feedback=Label(text="",font_size=dp(15),size_hint_y=None,height=dp(80)); box.add_widget(self.feedback)
    def check(self,*_):
        q=self.questions[self.index]; ok=answers_match(self.answer.text,q["answer"])
        self.correct+=int(ok)
        MasteryEngine(self.app.student).score(q["topic"],ok,q["difficulty"])
        s=self.app.student; s["today_done"]=s.get("today_done",0)+1; s["xp"]=s.get("xp",0)+(10 if ok else 3); s["level"]=1+s["xp"]//500
        self.feedback.text=("✓ Correct\n"+q["explanation"]) if ok else ("✗ Not quite\nAnswer: "+q["answer"]+"\n"+q["explanation"])
        save_student(self.app); self.index+=1
        if self.index>=len(self.questions):
            Clock.schedule_once(lambda dt:self.finish(),1.5)
        else: Clock.schedule_once(lambda dt:self.show_q(),1.5)
    def finish(self):
        s=self.app.student; s.setdefault("history",[]).append({"type":"practice","correct":self.correct,"total":len(self.questions),"date":datetime.now().isoformat()})
        save_student(self.app); self.app.go("home")

class PapersScreen(BaseScreen):
    def on_pre_enter(self):
        self.content.clear_widgets(); self.header("Paper Generator")
        box=self.scroll()
        box.add_widget(Label(text=f"Generate locally • Cost: 🪙 {ECONOMY['paper']}",font_size=dp(16),bold=True,size_hint_y=None,height=dp(35)))
        self.ptype=Spinner(text="Term / ATP Aligned",values=["Term / ATP Aligned","Weakness Recovery","Strength Challenge","Diagnostic","Mock Exam","Custom Topic Paper"],size_hint_y=None,height=dp(50)); box.add_widget(self.ptype)
        self.term=Spinner(text=str(self.app.student.get("term",1)),values=["1","2","3","4"],size_hint_y=None,height=dp(50)); box.add_widget(self.term)
        self.count=Spinner(text="15",values=["10","15","20","25"],size_hint_y=None,height=dp(50)); box.add_widget(self.count)
        box.add_widget(btn("GENERATE PAPER",self.generate,58))
        box.add_widget(title("Saved papers",18))
        for p in PaperEngine(ROOT).list_papers(self.app.student["code"])[:10]:
            box.add_widget(btn(f"{p['paper_id']} • {p['type']} • {p['marks']} marks",lambda _,pid=p["paper_id"]:self.view(pid),52))
    def generate(self,*_):
        cost=ECONOMY["weakness_paper"] if self.ptype.text=="Weakness Recovery" else ECONOMY["diagnostic"] if self.ptype.text=="Diagnostic" else ECONOMY["paper"]
        if self.app.student.get("credits",0)<cost:
            self.app.notice("Not enough credits",f"This offline paper costs {cost} credits.\nUse Developer Mode to simulate a pack purchase.")
            return
        add_tx(self.app,"PAPER_GENERATION",-cost,{"paper_type":self.ptype.text})
        paper,_=PaperEngine(ROOT).generate(self.app.student,self.ptype.text,int(self.term.text),count=int(self.count.text))
        save_student(self.app); self.app.paper=paper; self.app.go("paper")
    def view(self,pid): self.app.paper=PaperEngine(ROOT).load(pid)[0]; self.app.go("paper")

class PaperScreen(BaseScreen):
    def on_pre_enter(self):
        self.content.clear_widgets(); self.header("Paper")
        box=self.scroll(); p=self.app.paper
        if not p: return
        box.add_widget(title(f"{p['type']} • {p['marks']} marks",20))
        for q in p["questions"]:
            l=body(f"{q['number']}. {q['question']}\n\nMemo: {q['answer']}\nExplanation: {q['explanation']}",15); l.text_size=(dp(390),None); l.height=dp(max(110,len(q['question'])/45*28+90)); box.add_widget(l)

class ProfileScreen(BaseScreen):
    def on_pre_enter(self):
        self.content.clear_widgets(); self.header("Profile"); box=self.scroll(); s=self.app.student
        box.add_widget(title(s["name"],24)); box.add_widget(body(f"Code: {s['code']}\nLevel: {s.get('level',1)}\nXP: {s.get('xp',0):,}\nCredits: {s.get('credits',0):,}\nStreak: {s.get('streak',0)}",15))
        box.add_widget(title("Mastery",19))
        for t,m in sorted(s.get("mastery",{}).items(),key=lambda x:x[1]):
            box.add_widget(Label(text=f"{topic_name(t)} — {round(m*100)}%",font_size=dp(14),size_hint_y=None,height=dp(30)))

class SettingsScreen(BaseScreen):
    def on_pre_enter(self):
        self.content.clear_widgets(); self.header("Settings"); box=self.scroll()
        box.add_widget(btn("Enable Developer Mode",self.gate,52))
        box.add_widget(btn("Reset local student data",self.reset,52))
        box.add_widget(body("Learnly Offline V1 stores progress locally. No API, cloud database or payment gateway is used.",14))
    def gate(self,*_):
        self.app.go("dev_gate")
    def reset(self,*_):
        self.app.student=create_default_student(self.app.student["code"]); save_student(self.app); self.app.go("home")

class DevGateScreen(BaseScreen):
    def on_pre_enter(self):
        self.content.clear_widgets(); self.header("Developer Access")
        box=self.scroll(); box.add_widget(body("Developer Mode is for local testing only. Simulated purchases do not charge money.",15))
        self.code=TextInput(hint_text="DEV code",password=True,multiline=False,size_hint_y=None,height=dp(52)); box.add_widget(self.code)
        box.add_widget(btn("ACTIVATE",self.activate,54))
    def activate(self,*_):
        if self.code.text.strip()==DEV_CODE:
            self.app.student["dev_mode"]=True; save_student(self.app); self.app.go("dev")
        else: self.app.notice("Access denied","Incorrect developer code.")

class DevStoreScreen(BaseScreen):
    def on_pre_enter(self):
        self.content.clear_widgets(); self.header("🔧 DEV Store")
        box=self.scroll()
        box.add_widget(Label(text="DEVELOPER MODE • SIMULATED PURCHASES",font_size=dp(16),bold=True,size_hint_y=None,height=dp(38)))
        box.add_widget(Label(text=f"Balance: 🪙 {self.app.student.get('credits',0):,}",font_size=dp(22),bold=True,size_hint_y=None,height=dp(45)))
        for name,p in ECONOMY["packs"].items():
            box.add_widget(btn(f"{name}  •  R{p['price']:.2f}  •  +{p['credits']:,} credits",lambda _,n=name:self.buy(n),58))
        for amount in (1000,10000,100000):
            box.add_widget(btn(f"+{amount:,} TEST CREDITS",lambda _,a=amount:self.add(a),50))
        box.add_widget(btn("SET BALANCE",self.set_balance,50))
        box.add_widget(btn("RESET CREDITS",self.reset_credits,50))
        box.add_widget(title("Transaction ledger",19))
        for tx in reversed(self.app.student.get("credit_transactions",[])[:30]):
            box.add_widget(Label(text=f"{tx['type']}  {tx['credits']:+,}  → {tx['balance_after']:,}",font_size=dp(12),size_hint_y=None,height=dp(28)))
    def buy(self,name):
        p=ECONOMY["packs"][name]; add_tx(self.app,"DEV_PURCHASE",p["credits"],{"pack":name,"price":p["price"]}); self.on_pre_enter()
    def add(self,a): add_tx(self.app,"DEV_CREDIT_GRANT",a); self.on_pre_enter()
    def set_balance(self,*_):
        content=BoxLayout(orientation="vertical",padding=dp(10),spacing=dp(8)); ti=TextInput(text=str(self.app.student.get("credits",0)),input_filter="int",multiline=False)
        content.add_widget(ti); content.add_widget(btn("SET",lambda *_:(self._set(ti.text),pop.dismiss()),48)); pop=Popup(title="Set test balance",content=content,size_hint=(.85,.35)); pop.open()
    def _set(self,text):
        target=int(text or 0); current=self.app.student.get("credits",0); add_tx(self.app,"DEV_SET_BALANCE",target-current)
        self.on_pre_enter()
    def reset_credits(self,*_):
        add_tx(self.app,"DEV_RESET",-self.app.student.get("credits",0)); self.on_pre_enter()

class QuizScreen(BaseScreen):
    def on_pre_enter(self):
        self.content.clear_widgets(); self.header("Definitions Quiz")
        self.engine=DefinitionsQuizEngine(); self.q=self.engine.generate("math"); box=self.scroll()
        if not self.q: box.add_widget(body("Not enough vocabulary content.",15)); return
        box.add_widget(body(self.q["question"],18)); 
        for opt in self.q["options"]: box.add_widget(btn(opt,lambda _,x=opt:self.answer(x),54))
    def answer(self,x):
        self.app.notice("Correct" if x==self.q["answer"] else "Try again",f"Answer: {self.q['answer']}")
        if x==self.q["answer"]:
            self.app.student["xp"]=self.app.student.get("xp",0)+20; save_student(self.app)

class WeaknessScreen(PracticeScreen):
    def on_pre_enter(self):
        self.content.clear_widgets(); self.header("Weakness Training")
        box=self.scroll(); ad=AdaptiveEngine(self.app.student)
        weakest=ad.choose_topic("weakness")
        box.add_widget(title("Weakest topic",20)); box.add_widget(body(topic_name(weakest)+f" • {round(self.app.student['mastery'].get(weakest,.5)*100)}%",18))
        box.add_widget(btn("START 10-QUESTION RECOVERY",lambda *_:self.start("weakness"),58))
        box.add_widget(body("The offline adaptive engine selects lower-mastery topics and adjusts difficulty locally.",14))

class LearnlyApp(App):
    def build(self):
        Window.softinput_mode="below_target"
        self.student=None; self.student_path=None; self.topic_id=None; self.paper=None
        self.practice_mode="mixed"; self.practice_topics=[]; self.practice_count=10; self.practice_diff="Standard"
        self.mastery=None
        sm=ScreenManager(transition=SlideTransition()); self.sm=sm
        screens={"login":LoginScreen(),"home":HomeScreen(),"learn":LearnScreen(),"topic":TopicScreen(),
                 "practice":PracticeScreen(),"session":SessionScreen(),"papers":PapersScreen(),"paper":PaperScreen(),
                 "profile":ProfileScreen(),"settings":SettingsScreen(),"dev_gate":DevGateScreen(),
                 "dev":DevStoreScreen(),"quiz":QuizScreen(),"weakness":WeaknessScreen()}
        for name,screen in screens.items(): screen.name=name; sm.add_widget(screen)
        return sm
    def go(self,name):
        if name not in self.sm.screen_names: name="home"
        if self.student: self.mastery=MasteryEngine(self.student); save_student(self)
        self.sm.current=name
    def notice(self,title_text,message):
        Popup(title=title_text,content=Label(text=message,font_size=dp(15)),size_hint=(.85,.4)).open()
    def on_start(self): self.go("login")
    def on_stop(self): save_student(self)

if __name__=="__main__": LearnlyApp().run()
