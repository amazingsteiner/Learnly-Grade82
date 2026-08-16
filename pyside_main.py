import json, random, sys
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox, QSpinBox, QProgressBar, QScrollArea, QMessageBox

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'; STUDENTS=DATA/'students'; PAPERS=DATA/'papers'
CURRICULUM=ROOT/'content'/'curriculum'/'grade_map.json'
NOTES=ROOT/'content'/'notes'/'grade8_notes.json'
STUDENTS.mkdir(parents=True,exist_ok=True); PAPERS.mkdir(parents=True,exist_ok=True)
ACCESS='children of the sun'

def load_json(path,default):
    try:return json.loads(Path(path).read_text(encoding='utf-8'))
    except Exception:return default

def curriculum():return load_json(CURRICULUM,{'grades':{}})
def safe_code(x):return ''.join(c for c in x.upper() if c.isalnum() or c in '_-') or 'STUDENT'
def student_file(code):return STUDENTS/(safe_code(code)+'.json')
def topics(grade):return curriculum().get('grades',{}).get(grade,{}).get('topics',[])
def save(s):student_file(s['code']).write_text(json.dumps(s,indent=2,ensure_ascii=False),encoding='utf-8')
def sync_grade(s):
    allowed=curriculum().get('grades',{}).get(s['grade'],{}).get('topic_ids',[]); m=s.setdefault('mastery',{})
    for t in allowed:m.setdefault(t,0.5)
    s['mastery']={k:v for k,v in m.items() if k in allowed}
def load_student(code,grade,name=''):
    s={'code':safe_code(code),'name':name or safe_code(code),'grade':grade,'xp':0,'level':1,'daily_goal':10,'today_done':0,'scaling':'Adaptive','mastery':{}}
    p=student_file(code)
    if p.exists():
        try:s.update(json.loads(p.read_text(encoding='utf-8')))
        except Exception:pass
    s['grade']=grade; sync_grade(s); save(s); return s
def diff_for(s,tid):
    m=s['mastery'].get(tid,0.5); mode=s.get('scaling','Adaptive')
    if mode=='Foundation':return 1
    if mode=='Standard':return 2
    if mode=='Challenge':return 3 if m>=0.4 else 2
    return 1 if m<0.4 else 2 if m<0.75 else 3

class NumericKeyboard(QWidget):
    def __init__(self,target):
        super().__init__(); self.target=target; root=QVBoxLayout(self)
        for keys in [['1','2','3','←'],['4','5','6','C'],['7','8','9','−'],['0','.','/','+']]:
            row=QHBoxLayout()
            for k in keys:
                b=QPushButton(k); b.setMinimumHeight(42); b.clicked.connect(lambda _,x=k:self.press(x)); row.addWidget(b)
            root.addLayout(row)
    def press(self,k):
        if k=='C':self.target.clear()
        elif k=='←':self.target.setText(self.target.text()[:-1])
        else:self.target.insert(k.replace('−','-'))

class Page(QWidget):
    def __init__(self,app,title):
        super().__init__();self.app=app;outer=QVBoxLayout(self);top=QHBoxLayout();back=QPushButton('← Home');back.clicked.connect(app.home);top.addWidget(back);t=QLabel(title);t.setObjectName('title');top.addWidget(t,1);outer.addLayout(top)
        scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff);self.body=QWidget();self.layout=QVBoxLayout(self.body);scroll.setWidget(self.body);outer.addWidget(scroll,1)
    def add(self,w):self.layout.addWidget(w)
    def clear(self):
        while self.layout.count():
            x=self.layout.takeAt(0)
            if x.widget():x.widget().deleteLater()

class Login(Page):
    def __init__(self,app):
        super().__init__(app,'Learnly');self.add(QLabel('Learnly Mathematics\nPySide6 • Pydroid 3 • Offline'))
        self.access=QLineEdit();self.access.setPlaceholderText('Development access code');self.access.setEchoMode(QLineEdit.Password);self.add(self.access)
        self.code=QLineEdit();self.code.setPlaceholderText('Student code');self.add(self.code)
        self.name=QLineEdit();self.name.setPlaceholderText('Student name');self.add(self.name)
        self.grade=QComboBox();self.grade.addItems(['Grade R']+[f'Grade {i}' for i in range(1,10)]);self.grade.setCurrentText('Grade 8');self.add(self.grade)
        b=QPushButton('START LEARNLY');b.clicked.connect(self.login);self.add(b);self.msg=QLabel();self.add(self.msg)
    def login(self):
        if self.access.text().strip().lower()!=ACCESS:self.msg.setText('Access code is incorrect.');return
        if not self.code.text().strip():self.msg.setText('Enter a student code.');return
        self.app.student=load_student(self.code.text(),self.grade.currentText(),self.name.text().strip());self.app.home()

class Home(Page):
    def __init__(self,app):super().__init__(app,'Learnly');self.refresh()
    def refresh(self):
        self.clear();s=self.app.student;m=sum(s['mastery'].values())/max(1,len(s['mastery']))
        self.add(QLabel(f"Welcome, {s['name']}\n{s['grade']} Mathematics"));self.add(QLabel(f"Mastery {m*100:.0f}% • Level {s['level']} • XP {s['xp']}"))
        p=QProgressBar();p.setRange(0,s['daily_goal']);p.setValue(min(s['today_done'],s['daily_goal']));p.setFormat(f"Today's goal: {s['today_done']}/{s['daily_goal']}");self.add(p)
        self.add(QLabel(f"{len(topics(s['grade']))} curriculum-verified topics available."))
        for text,name in [('📚 Learn — pick a topic','learn'),('🎯 Practice — adaptive','practice'),('📝 Papers — Pillow worksheet','papers'),('⚙ Adjust learning','settings')]:
            b=QPushButton(text);b.clicked.connect(lambda _,n=name:self.app.show(n));self.add(b)

class Learn(Page):
    def __init__(self,app):super().__init__(app,'Learn • Pick a Topic');self.refresh()
    def refresh(self):
        self.clear();s=self.app.student;self.add(QLabel(f"Pick a topic for {s['grade']}. Only verified topics appear here."))
        for x in topics(s['grade']):
            tid=x['id'];b=QPushButton(f"{x['name']} • {s['mastery'].get(tid,.5)*100:.0f}%");b.clicked.connect(lambda _,t=tid:self.app.topic(t));self.add(b)

class Topic(Page):
    def __init__(self,app,tid):self.tid=tid;super().__init__(app,'Topic');self.refresh()
    def refresh(self):
        self.clear();d=load_json(NOTES,{}).get(self.tid,{})
        self.add(QLabel(d.get('title',self.tid.replace('_',' ').title())))
        for title,key in [('Simple explanation','note'),('How to do it','steps'),('Worked example','example'),('Tips & tricks','tips'),('Common mistakes','mistakes')]:
            if d.get(key):
                self.add(QLabel(title));x=QLabel(d[key]);x.setWordWrap(True);self.add(x)
        b=QPushButton('PRACTICE THIS TOPIC');b.clicked.connect(lambda:self.app.practice(self.tid));self.add(b)

class Practice(Page):
    def __init__(self,app,preset=None):
        self.preset=preset;super().__init__(app,'Practice');self.build()
    def build(self):
        self.clear();s=self.app.student;self.add(QLabel('Learnly checks the grade gate before generating every question.'))
        self.topic=QComboBox();[(self.topic.addItem(x['name'],x['id'])) for x in topics(s['grade'])];self.add(self.topic)
        if self.preset:
            i=self.topic.findData(self.preset)
            if i>=0:self.topic.setCurrentIndex(i)
        self.mode=QComboBox();self.mode.addItems(['Adaptive','Foundation','Standard','Challenge']);self.add(self.mode)
        self.q=QLabel('Press START.');self.q.setWordWrap(True);self.add(self.q);self.answer=QLineEdit();self.answer.setPlaceholderText('Your answer');self.add(self.answer);self.add(NumericKeyboard(self.answer))
        row=QHBoxLayout()
        for txt,fn in [('START',self.next),('CHECK',self.check),('HINT',self.hint)]:b=QPushButton(txt);b.clicked.connect(fn);row.addWidget(b)
        self.layout.addLayout(row);self.feedback=QLabel();self.feedback.setWordWrap(True);self.add(self.feedback)
    def next(self):
        tid=self.topic.currentData();allowed=curriculum().get('grades',{}).get(self.app.student['grade'],{}).get('topic_ids',[])
        if tid not in allowed:self.feedback.setText('BLOCKED: this topic is outside the selected grade.');return
        from engine.question_engine import QuestionEngine
        d={'Foundation':1,'Standard':2,'Challenge':3}.get(self.mode.currentText(),diff_for(self.app.student,tid))
        try:self.question=QuestionEngine().generate(tid,d)
        except Exception:self.question=None
        if not self.question:self.feedback.setText('No verified question is available yet. Nothing unsafe was shown.');return
        self.q.setText(self.topic.currentText()+'\n\n'+self.question['question']);self.answer.clear();self.feedback.setText(f"Difficulty level {d}")
    def check(self):
        if not hasattr(self,'question'):return
        ok=self.answer.text().replace(' ','').lower()==str(self.question['answer']).replace(' ','').lower();tid=self.topic.currentData();old=self.app.student['mastery'].get(tid,.5);self.app.student['mastery'][tid]=max(0,min(1,old+(0.05 if ok else -0.03)));self.app.student['today_done']+=1;self.app.student['xp']+=10 if ok else 3;self.app.student['level']=1+self.app.student['xp']//500;save(self.app.student);self.feedback.setText(('✓ Correct\n' if ok else f"✗ Answer: {self.question['answer']}\n")+self.question.get('explanation',''))
    def hint(self):
        if hasattr(self,'question'):self.feedback.setText('💡 '+self.question.get('hint','Use the rule for this topic.'))

class Papers(Page):
    def __init__(self,app):super().__init__(app,'Paper Generator');self.build()
    def build(self):
        self.clear();s=self.app.student;self.add(QLabel('Pillow creates the worksheet locally.'))
        self.topic=QComboBox();self.topic.addItem('Mixed',None);[(self.topic.addItem(x['name'],x['id'])) for x in topics(s['grade'])];self.add(self.topic)
        self.count=QSpinBox();self.count.setRange(5,30);self.count.setValue(10);self.add(QLabel('Number of questions'));self.add(self.count);b=QPushButton('GENERATE PNG PAPER');b.clicked.connect(self.generate);self.add(b);self.out=QLabel();self.out.setWordWrap(True);self.add(self.out)
    def generate(self):
        try:
            from engine.pillow_paper import make_paper
            path=make_paper(self.app.student,self.topic.currentData(),self.count.value());self.out.setText('✓ Paper created:\n'+str(path))
        except Exception as e:self.out.setText('Paper generation error:\n'+str(e))

class Settings(Page):
    def __init__(self,app):super().__init__(app,'Adjust Learning');self.build()
    def build(self):
        self.clear();s=self.app.student;self.add(QLabel('Adjust the experience. The grade curriculum remains protected.'))
        self.goal=QSpinBox();self.goal.setRange(1,100);self.goal.setValue(s['daily_goal']);self.add(QLabel('Daily goal'));self.add(self.goal)
        self.scale=QComboBox();self.scale.addItems(['Adaptive','Gentle','Standard','Challenge']);self.scale.setCurrentText(s.get('scaling','Adaptive'));self.add(QLabel('Difficulty scaling'));self.add(self.scale)
        self.grade=QComboBox();self.grade.addItems(['Grade R']+[f'Grade {i}' for i in range(1,10)]);self.grade.setCurrentText(s['grade']);self.add(QLabel('School grade'));self.add(self.grade)
        b=QPushButton('SAVE AND RECHECK CURRICULUM');b.clicked.connect(self.save_settings);self.add(b)
    def save_settings(self):
        s=self.app.student;s['daily_goal']=self.goal.value();s['scaling']=self.scale.currentText();s['grade']=self.grade.currentText();sync_grade(s);save(s);QMessageBox.information(self,'Updated','Your settings were saved and the allowed topics were rechecked.');self.app.home()

class Learnly(QMainWindow):
    def __init__(self):
        super().__init__();self.setWindowTitle('Learnly • PySide6');self.resize(430,800);self.student=None;self.stack=QStackedWidget();self.setCentralWidget(self.stack);self.pages={};self.login_page=Login(self);self.stack.addWidget(self.login_page);self.setStyleSheet('QWidget{font-size:16px} QLabel#title{font-size:24px;font-weight:700} QPushButton{min-height:48px;padding:7px} QLineEdit,QComboBox,QSpinBox{min-height:42px;padding:5px}')
    def home(self):self.show('home')
    def show(self,name):
        if name not in self.pages:
            cls={'home':Home,'learn':Learn,'practice':Practice,'papers':Papers,'settings':Settings}[name];self.pages[name]=cls(self);self.stack.addWidget(self.pages[name])
        p=self.pages[name];getattr(p,'refresh',lambda:None)();self.stack.setCurrentWidget(p)
    def topic(self,tid):
        p=Topic(self,tid);self.stack.addWidget(p);self.stack.setCurrentWidget(p)
    def practice(self,tid=None):
        p=Practice(self,tid);self.stack.addWidget(p);self.stack.setCurrentWidget(p)

if __name__=='__main__':
    app=QApplication(sys.argv);app.setApplicationName('Learnly');w=Learnly();w.show();sys.exit(app.exec())
