import json
from pathlib import Path
from kivy.app import App
from kivy.metrics import dp, sp
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
from engine.grade_safe_questions import GradeSafeQuestion

ROOT=Path(__file__).resolve().parent
CURRICULUM=ROOT/"content/curriculum/grade_map.json"
NOTES=ROOT/"content/notes/grade8_notes.json"

def read(path, default):
    try:return json.loads(path.read_text(encoding="utf-8"))
    except:return default

def curriculum():return read(CURRICULUM,{"grades":{}})
def notes():return read(NOTES,{})
def clean_code(v):return "".join(c for c in v.upper() if c.isalnum() or c in "_-") or "STUDENT"

class LButton(Button):
    def __init__(self,**kw):
        super().__init__(**kw); self.size_hint_y=None; self.height=dp(52); self.font_size=sp(16); self.background_normal=""; self.background_color=(.12,.28,.46,1)

class MathKeyboard(GridLayout):
    def __init__(self,target,**kw):
        super().__init__(**kw); self.cols=4; self.spacing=dp(4); self.size_hint_y=None; self.height=dp(188); self.target=target
        for k in ["1","2","3","⌫","4","5","6","C","7","8","9","−","0",".","/","+"]:
            b=Button(text=k,font_size=sp(18),background_normal="",background_color=(.18,.22,.28,1)); b.bind(on_release=lambda x:self.press(x.text)); self.add_widget(b)
    def press(self,k):
        if k=="C":self.target.text=""
        elif k=="⌫":self.target.text=self.target.text[:-1]
        else:self.target.insert_text(k.replace("−","-"))

class Base(Screen):
    def page(self,title,body,back=True):
        root=BoxLayout(orientation="vertical",padding=dp(12),spacing=dp(8)); h=BoxLayout(size_hint_y=None,height=dp(50),spacing=dp(8))
        if back:
            b=LButton(text="‹"); b.size_hint_x=None;b.width=dp(50);b.bind(on_release=lambda *_:setattr(self.manager,"current","home"));h.add_widget(b)
        h.add_widget(Label(text=title,font_size=sp(22),bold=True));root.add_widget(h);root.add_widget(body);self.clear_widgets();self.add_widget(root)

class Login(Base):
    def on_pre_enter(self,*a):
        r=BoxLayout(orientation="vertical",padding=dp(24),spacing=dp(12));r.add_widget(Widget());r.add_widget(Label(text="LEARNLY",font_size=sp(36),bold=True,size_hint_y=None,height=dp(55)));r.add_widget(Label(text="Mathematics • Offline • Adaptive",font_size=sp(17),size_hint_y=None,height=dp(34)))
        self.code=TextInput(hint_text="Student code",multiline=False,size_hint_y=None,height=dp(52),font_size=sp(18));r.add_widget(self.code)
        self.grade=Spinner(text="Grade 8",values=["Grade R"]+[f"Grade {i}" for i in range(1,10)],size_hint_y=None,height=dp(52));r.add_widget(self.grade)
        b=LButton(text="START LEARNLY");b.bind(on_release=self.login);r.add_widget(b);self.status=Label(text="",size_hint_y=None,height=dp(35));r.add_widget(self.status);r.add_widget(Widget());self.clear_widgets();self.add_widget(r)
    def login(self,*a):
        if not self.code.text.strip():self.status.text="Enter your student code.";return
        app=App.get_running_app();app.ensure();app.student=app.load_student(clean_code(self.code.text),self.grade.text);self.manager.current="home"

class Home(Base):
    def on_pre_enter(self,*a):
        app=App.get_running_app();s=app.student; m=sum(s.get("mastery",{}).values())/max(1,len(s.get("mastery",{})));body=BoxLayout(orientation="vertical",spacing=dp(8))
        body.add_widget(Label(text=f"Welcome, {s['name']}",font_size=sp(25),bold=True,size_hint_y=None,height=dp(42)));body.add_widget(Label(text=f"{s['grade']} Mathematics • Level {s['level']} • {s['xp']} XP",size_hint_y=None,height=dp(30)));body.add_widget(ProgressBar(max=1,value=m,size_hint_y=None,height=dp(12)));body.add_widget(Label(text=f"Mastery {m*100:.0f}% • Daily goal {s['today_done']}/{s['daily_goal']}",size_hint_y=None,height=dp(30)))
        scroll=ScrollView();g=GridLayout(cols=1,spacing=dp(8),size_hint_y=None);g.bind(minimum_height=g.setter("height"))
        for text,screen in [("📚 LEARN — notes, examples & tricks","learn"),("🎯 PRACTICE — pick a topic","practice"),("📝 PAPERS — printable worksheets","papers"),("📊 PROGRESS — mastery","progress"),("⚙ SETTINGS — adjust Learnly","settings")]:
            b=LButton(text=text);b.bind(on_release=lambda _,n=screen:setattr(self.manager,"current",n));g.add_widget(b)
        scroll.add_widget(g);body.add_widget(scroll);self.page("Learnly",body,False)

class Learn(Base):
    def on_pre_enter(self,*a):
        app=App.get_running_app();items=curriculum().get("grades",{}).get(app.student["grade"],{}).get("topics",[]);body=BoxLayout(orientation="vertical",spacing=dp(7));body.add_widget(Label(text=f"Pick a topic • {app.student['grade']}",font_size=sp(19),bold=True,size_hint_y=None,height=dp(36)))
        scroll=ScrollView();g=GridLayout(cols=1,spacing=dp(7),size_hint_y=None);g.bind(minimum_height=g.setter("height"))
        for x in items:
            tid=x["id"];b=LButton(text=f"{x['name']}   {app.student.get('mastery',{}).get(tid,.5)*100:.0f}%");b.bind(on_release=lambda _,t=tid:self.topic(t));g.add_widget(b)
        scroll.add_widget(g);body.add_widget(scroll);self.page("Learn",body)
    def topic(self,tid):
        d=notes().get(tid,{"title":tid.replace('_',' ').title()});body=BoxLayout(orientation="vertical",spacing=dp(7));scroll=ScrollView();g=BoxLayout(orientation="vertical",spacing=dp(8),size_hint_y=None);g.bind(minimum_height=g.setter("height"));g.add_widget(Label(text=d.get("title",tid),font_size=sp(23),bold=True,size_hint_y=None,height=dp(45)))
        for key,label in [("note","NOTES"),("tips","TIPS & TRICKS"),("steps","HOW TO DO IT"),("example","WORKED EXAMPLE"),("mistakes","COMMON MISTAKES"),("check","QUICK CHECK")]:
            if d.get(key):g.add_widget(Label(text=label,font_size=sp(17),bold=True,size_hint_y=None,height=dp(30)));g.add_widget(Label(text=str(d[key]),font_size=sp(14),text_size=(dp(370),None),size_hint_y=None,height=dp(105)))
        b=LButton(text="PRACTICE THIS TOPIC");b.bind(on_release=lambda *_:self.practice(tid));g.add_widget(b);scroll.add_widget(g);body.add_widget(scroll);self.page("Topic",body)
    def practice(self,tid):App.get_running_app().practice_topic=tid;self.manager.current="practice"

class Practice(Base):
    def on_pre_enter(self,*a):
        app=App.get_running_app();items=curriculum().get("grades",{}).get(app.student["grade"],{}).get("topics",[]);self.ids_map={x["name"]:x["id"] for x in items};names=list(self.ids_map);body=BoxLayout(orientation="vertical",spacing=dp(7));default=next((x["name"] for x in items if x["id"]==getattr(app,"practice_topic",None)),names[0] if names else "No topic")
        self.topic=Spinner(text=default,values=names,size_hint_y=None,height=dp(50));body.add_widget(self.topic);self.diff=Spinner(text="Adaptive",values=["Adaptive","Foundation","Standard","Advanced"],size_hint_y=None,height=dp(50));body.add_widget(self.diff);self.qtext=Label(text="Pick a topic and press START",font_size=sp(19),text_size=(dp(380),None),size_hint_y=None,height=dp(80));body.add_widget(self.qtext);self.answer=TextInput(hint_text="Answer",multiline=False,size_hint_y=None,height=dp(52),font_size=sp(20));body.add_widget(self.answer);body.add_widget(MathKeyboard(self.answer));row=BoxLayout(size_hint_y=None,height=dp(52),spacing=dp(6))
        for t,f in [("START",self.start),("CHECK",self.check),("HINT",self.hint)]:b=LButton(text=t);b.bind(on_release=f);row.add_widget(b)
        body.add_widget(row);self.feedback=Label(text="",text_size=(dp(380),None),size_hint_y=None,height=dp(90));body.add_widget(self.feedback);self.page("Practice",body)
    def start(self,*a):
        app=App.get_running_app();tid=self.ids_map.get(self.topic.text);allowed=curriculum()["grades"].get(app.student["grade"],{}).get("topic_ids",[])
        if tid not in allowed:self.feedback.text="Blocked: this topic is outside the student's selected grade.";return
        d={"Foundation":1,"Standard":2,"Advanced":3}.get(self.diff.text,app.recommended(tid));self.topic_id=tid
        try:self.q=QuestionEngine().generate(tid,d) if app.student["grade"] in ("Grade 8","Grade 9") else GradeSafeQuestion().generate(app.student["grade"],tid,d)
        except Exception:self.q=GradeSafeQuestion().generate(app.student["grade"],tid,d)
        if not self.q:self.feedback.text="This topic has no verified question generator yet; Learnly will not guess.";return
        self.qtext.text=self.q["question"];self.answer.text="";self.feedback.text=f"{self.q['topic_name']} • Difficulty {self.q['difficulty']}"
    def check(self,*a):
        if not hasattr(self,"q"):return
        got=self.answer.text.strip().replace("−","-").replace(" ","").lower();exp=str(self.q["answer"]).replace(" ","").lower();ok=got==exp;app=App.get_running_app();old=app.student["mastery"].get(self.topic_id,.5);app.student["mastery"][self.topic_id]=max(0,min(1,old+(.05 if ok else -.03)));app.student["today_done"]+=1;app.student["xp"]+=10 if ok else 3;app.student["level"]=1+app.student["xp"]//500;app.save();self.feedback.text=("✓ Correct\n" if ok else f"✗ Answer: {self.q['answer']}\n")+self.q.get("explanation","")
    def hint(self,*a):
        if hasattr(self,"q"):self.feedback.text="💡 "+self.q.get("hint","Review the rule in Learn.")

class Papers(Base):
    def on_pre_enter(self,*a):
        app=App.get_running_app();items=curriculum()["grades"].get(app.student["grade"],{}).get("topics",[]);self.map={x["name"]:x["id"] for x in items};body=BoxLayout(orientation="vertical",spacing=dp(8));self.topic=Spinner(text="Mixed",values=["Mixed"]+list(self.map),size_hint_y=None,height=dp(50));body.add_widget(self.topic);self.count=Spinner(text="10",values=["5","10","15","20","30"],size_hint_y=None,height=dp(50));body.add_widget(self.count);b=LButton(text="GENERATE PNG PAPER");b.bind(on_release=self.generate);body.add_widget(b);self.out=Label(text="Papers are rendered offline with Pillow.",text_size=(dp(380),None));body.add_widget(self.out);self.page("Paper Generator",body)
    def generate(self,*a):
        from engine.pillow_paper import make_paper
        tid=self.map.get(self.topic.text);path=make_paper(App.get_running_app().student,tid,int(self.count.text));self.out.text=f"✓ Created\n{path}"

class Progress(Base):
    def on_pre_enter(self,*a):
        s=App.get_running_app().student;body=BoxLayout(orientation="vertical");scroll=ScrollView();g=GridLayout(cols=1,size_hint_y=None);g.bind(minimum_height=g.setter("height"));
        for k,v in sorted(s.get("mastery",{}).items(),key=lambda x:x[1]):g.add_widget(Label(text=f"{k.replace('_',' ').title()}   {v*100:.0f}%",size_hint_y=None,height=dp(35)))
        scroll.add_widget(g);body.add_widget(scroll);self.page("Progress",body)

class Settings(Base):
    def on_pre_enter(self,*a):
        s=App.get_running_app().student;body=BoxLayout(orientation="vertical",spacing=dp(8));self.goal=Spinner(text=str(s["daily_goal"]),values=["5","10","20","30","50"],size_hint_y=None,height=dp(50));body.add_widget(Label(text="Daily goal"));body.add_widget(self.goal);self.scale=Spinner(text=s.get("scaling","Adaptive"),values=["Adaptive","Gentle","Standard","Challenge"],size_hint_y=None,height=dp(50));body.add_widget(Label(text="Question scaling"));body.add_widget(self.scale);self.grade=Spinner(text=s["grade"],values=["Grade R"]+[f"Grade {i}" for i in range(1,10)],size_hint_y=None,height=dp(50));body.add_widget(Label(text="Grade"));body.add_widget(self.grade);b=LButton(text="SAVE");b.bind(on_release=self.save);body.add_widget(b);self.page("Settings",body)
    def save(self,*a):
        app=App.get_running_app();app.student["daily_goal"]=int(self.goal.text);app.student["scaling"]=self.scale.text;app.student["grade"]=self.grade.text;app.sync();app.save();self.manager.current="home"

class Learnly(App):
    def build(self):
        self.student=None;self.practice_topic=None;sm=ScreenManager();
        for c,n in [(Login,"login"),(Home,"home"),(Learn,"learn"),(Practice,"practice"),(Papers,"papers"),(Progress,"progress"),(Settings,"settings")]:sm.add_widget(c(name=n))
        return sm
    def ensure(self):
        self.data=Path(self.user_data_dir);(self.data/"students").mkdir(parents=True,exist_ok=True);(self.data/"papers").mkdir(parents=True,exist_ok=True)
    def load_student(self,code,grade):
        self.ensure();p=self.data/"students"/(code+".json");s={"code":code,"name":f"Student {code}","grade":grade,"daily_goal":20,"today_done":0,"xp":0,"level":1,"scaling":"Adaptive","mastery":{}}
        if p.exists():
            try:s.update(json.loads(p.read_text(encoding="utf-8")))
            except:pass
        s["grade"]=grade;self.student=s;self.sync();self.save();return s
    def sync(self):
        ids=curriculum().get("grades",{}).get(self.student["grade"],{}).get("topic_ids",[]);m=self.student.setdefault("mastery",{});[m.setdefault(t,.5) for t in ids];self.student["mastery"]={k:v for k,v in m.items() if k in ids}
    def save(self):
        self.ensure();(self.data/"students"/(clean_code(self.student["code"])+".json")).write_text(json.dumps(self.student,indent=2),encoding="utf-8")
    def recommended(self,tid):
        v=self.student.get("mastery",{}).get(tid,.5);return 1 if v<.4 else 2 if v<.7 else 3 if v<.9 else 4

if __name__=="__main__":Learnly().run()
