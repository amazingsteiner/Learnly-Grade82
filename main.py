import sys, json, random, math
from pathlib import Path
from datetime import datetime
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication,QMainWindow,QWidget,QVBoxLayout,QLabel,QPushButton,QLineEdit,QMessageBox,QStackedWidget,QComboBox,QSpinBox,QProgressBar
ROOT=Path(__file__).resolve().parent; DATA=ROOT/'data'; STUDENTS=DATA/'students'; PAPERS=DATA/'papers'; STUDENTS.mkdir(parents=True,exist_ok=True); PAPERS.mkdir(parents=True,exist_ok=True)
ACCESS='children of the sun'; DEV_MODE=True
TOPICS=['Whole Numbers','Integers','Exponents','Patterns','Algebraic Expressions','Algebraic Equations','Geometry','Pythagoras','Area & Perimeter','Financial Maths','Transformations','Data Handling','Probability']
DEFAULT={'code':'','name':'','grade':8,'term':1,'xp':0,'streak':0,'daily_goal':20,'today_done':0,'mastery':{},'papers':[],'credits':1000,'credit_transactions':[],'dev_mode':False}
def sp(c): return STUDENTS/(''.join(x for x in c.upper() if x.isalnum() or x in '_-')+'.json')
def save(s): sp(s['code']).write_text(json.dumps(s,indent=2,ensure_ascii=False),encoding='utf-8')
def load(c):
 s=dict(DEFAULT); p=sp(c)
 if p.exists():
  try:s.update(json.loads(p.read_text(encoding='utf-8')))
  except:pass
 s['code']=c.upper();s['name']=s.get('name') or s['code'];s['mastery']=dict(s.get('mastery',{}))
 for t in TOPICS:s['mastery'].setdefault(t,.5)
 save(s);return s
def credit(s,n,k):
 if s['credits']+n<0:return False
 b=s['credits'];s['credits']+=n;s['credit_transactions'].append({'type':k,'credits':n,'before':b,'after':s['credits'],'time':datetime.now().isoformat()});save(s);return True
class Engine:
 def q(self,t):
  if t=='Algebraic Equations':
   a=random.randint(2,8);x=random.randint(2,12);b=random.randint(1,12);c=a*x+b;return f'Solve: {a}x + {b} = {c}',str(x),f'{a}x={c-b}; x={x}.'
  if t=='Exponents':
   a=random.randint(2,5);x=random.randint(1,4);y=random.randint(1,4);return f'Simplify: {a}^{x} × {a}^{y}',f'{a}^{x+y}','Same base: add exponents.'
  if t=='Pythagoras':return 'Right triangle legs are 3 and 4. Find c.','5','c²=a²+b².'
  if t=='Probability':return 'A bag has 2 red and 3 blue counters. Find P(red).','2/5','Favourable outcomes ÷ total outcomes.'
  if t=='Data Handling':
   v=[2,4,6,8,10];return 'Find the mean: '+', '.join(map(str,v)),'6','Add and divide by 5.'
  a=random.randint(3,12);b=random.randint(2,10);return f'Calculate: {a} × {b}',str(a*b),f'{a} × {b} = {a*b}.'
class Login(QWidget):
 def __init__(self,a):
  super().__init__();self.a=a;l=QVBoxLayout(self);l.addStretch();z=QLabel('LEARNLY\nGRADE 8 OFFLINE');z.setAlignment(Qt.AlignCenter);z.setStyleSheet('font-size:32px;font-weight:bold');l.addWidget(z);self.ac=QLineEdit();self.ac.setPlaceholderText('Access code');self.ac.setEchoMode(QLineEdit.Password);l.addWidget(self.ac);self.sc=QLineEdit();self.sc.setPlaceholderText('Student code');l.addWidget(self.sc);b=QPushButton('ENTER LEARNLY');b.clicked.connect(self.login);l.addWidget(b);l.addStretch()
 def login(self):
  if self.ac.text().strip().lower()!=ACCESS:return QMessageBox.warning(self,'Access denied','Incorrect access code.')
  if not self.sc.text().strip():return
  self.a.student=load(self.sc.text().strip());self.a.show('home')
class Page(QWidget):
 def __init__(self,a,title):
  super().__init__();self.a=a;l=QVBoxLayout(self);b=QPushButton('← Home');b.clicked.connect(lambda:a.show('home'));l.addWidget(b);l.addWidget(QLabel(title));self.l=l
 def add(self,w):self.l.addWidget(w)
class Home(Page):
 def __init__(self,a):super().__init__(a,'Learnly');self.refresh()
 def refresh(self):
  while self.l.count():self.l.takeAt(0).widget().deleteLater()
  s=self.a.student;self.add(QLabel(f"{s['name']}\n🪙 {s['credits']:,} Credits   ⭐ {s['xp']} XP"));p=QProgressBar();p.setRange(0,s['daily_goal']);p.setValue(min(s['today_done'],s['daily_goal']));p.setFormat(f"Daily goal {s['today_done']}/{s['daily_goal']}");self.add(p)
  for t,n in [('📚 Learn','learn'),('🧠 Practice','practice'),('📝 Paper Generator','papers'),('📐 Maths Tools','tools'),('⚙ Settings','settings')]:b=QPushButton(t);b.clicked.connect(lambda _,n=n:self.a.show(n));self.add(b)
  if s.get('dev_mode'):b=QPushButton('🔧 DEV STORE');b.clicked.connect(lambda:self.a.show('dev'));self.add(b)
  elif DEV_MODE:b=QPushButton('Developer Mode');b.clicked.connect(self.enable);self.add(b)
 def enable(self):
  if QMessageBox.question(self,'Developer Mode','Enable developer tools?')==QMessageBox.Yes:self.a.student['dev_mode']=True;save(self.a.student);self.refresh()
class Learn(Page):
 def __init__(self,a):super().__init__(a,'Learn');
 def showEvent(self,e):
  for t in TOPICS:b=QPushButton(f'📖 {t} • {round(self.a.student["mastery"][t]*100)}%');b.clicked.connect(lambda _,t=t:QMessageBox.information(self,t,'Core concept, rules and worked examples are available offline.'));self.add(b)
class Practice(Page):
 def __init__(self,a):
  super().__init__(a,'Practice');self.e=Engine();self.mode=QComboBox();self.mode.addItems(['Recommended','Weakness','Strength','Mixed']);self.add(self.mode);self.q=QLabel();self.q.setWordWrap(True);self.add(self.q);self.inp=QLineEdit();self.inp.setPlaceholderText('Your answer');self.add(self.inp);self.f=QLabel();self.f.setWordWrap(True);self.add(self.f);b=QPushButton('CHECK');b.clicked.connect(self.check);self.add(b);n=QPushButton('NEXT');n.clicked.connect(self.next);self.add(n);self.next()
 def next(self):
  m=self.a.student['mastery'];mode=self.mode.currentText().lower();t=min(m,key=m.get) if mode=='weakness' else max(m,key=m.get) if mode=='strength' else random.choice(TOPICS);self.topic=t;self.question,self.answer,self.exp=self.e.q(t);self.q.setText(t+'\n\n'+self.question);self.inp.clear();self.f.clear()
 def check(self):
  ok=self.inp.text().strip().lower()==self.answer.lower();m=self.a.student['mastery'][self.topic];self.a.student['mastery'][self.topic]=max(0,min(1,m+(0.05 if ok else -0.03)));self.a.student['today_done']+=1;self.a.student['xp']+=10 if ok else 3;save(self.a.student);self.f.setText(('✓ Correct\n' if ok else '✗ Not quite\nAnswer: '+self.answer+'\n')+self.exp)
class Papers(Page):
 def __init__(self,a):super().__init__(a,'Paper Generator');self.e=Engine();self.n=QSpinBox();self.n.setRange(5,50);self.n.setValue(20);self.add(self.n);b=QPushButton('GENERATE PAPER • 400 CREDITS');b.clicked.connect(self.gen);self.add(b);self.out=QLabel();self.out.setWordWrap(True);self.add(self.out)
 def gen(self):
  s=self.a.student
  if not credit(s,-400,'PAPER_GENERATION'):return QMessageBox.warning(self,'Credits','Not enough credits.')
  qs=[self.e.q(random.choice(TOPICS)) for _ in range(self.n.value())];pid='P'+datetime.now().strftime('%Y%m%d%H%M%S%f');(PAPERS/(pid+'.json')).write_text(json.dumps({'id':pid,'student':s['code'],'questions':qs},indent=2),encoding='utf-8');s['papers'].append(pid);save(s);self.out.setText(f'✓ Paper generated\n{pid}\nBalance: {s["credits"]:,}\nSaved offline.')
class Tools(Page):
 def __init__(self,a):super().__init__(a,'Maths Tools');b=QPushButton('🧮 MENTAL MATHS');b.clicked.connect(lambda:QMessageBox.information(self,'Mental Maths','×25 = ×100 ÷4\n×50 = ×100 ÷2\n×9 = ×10 − original\n10% = ÷10'));self.add(b)
class Settings(Page):
 def __init__(self,a):super().__init__(a,'Settings');self.g=QSpinBox();self.g.setRange(1,200);self.g.setValue(a.student['daily_goal']);self.add(QLabel('Daily goal'));self.add(self.g);b=QPushButton('SAVE');b.clicked.connect(self.save);self.add(b)
 def save(self):self.a.student['daily_goal']=self.g.value();save(self.a.student);QMessageBox.information(self,'Saved','Settings saved.')
class Dev(Page):
 def __init__(self,a):super().__init__(a,'🔧 DEVELOPER MODE');self.bal=QLabel();self.add(QLabel('OFFLINE • DEV BUILD'));self.add(self.bal);self.refresh()
 def refresh(self):
  self.bal.setText(f'Current balance: {self.a.student["credits"]:,}')
  for t,n in [('+1,000 Credits',1000),('+10,000 Credits',10000),('+30,000 Credits',30000),('Remove 1,000',-1000)]:b=QPushButton(t);b.clicked.connect(lambda _,n=n:self.change(n));self.add(b)
 def change(self,n):
  if credit(self.a.student,n,'DEV_PURCHASE' if n>0 else 'DEV_ADJUST'):self.bal.setText(f'Current balance: {self.a.student["credits"]:,}')
class Learnly(QMainWindow):
 def __init__(self):
  super().__init__();self.setWindowTitle('Learnly Grade 8');self.resize(430,800);self.student=None;self.stack=QStackedWidget();self.setCentralWidget(self.stack);self.stack.addWidget(Login(self));self.screens={};self.extra=[];self.setStyleSheet('QWidget{font-size:16px} QPushButton{min-height:48px;padding:8px} QLineEdit,QComboBox,QSpinBox{min-height:42px}')
 def show(self,n):
  if n not in self.screens:self.screens[n]={'home':Home,'learn':Learn,'practice':Practice,'papers':Papers,'tools':Tools,'settings':Settings,'dev':Dev}[n](self);self.stack.addWidget(self.screens[n])
  w=self.screens[n];self.stack.setCurrentWidget(w);w.refresh() if hasattr(w,'refresh') else None
if __name__=='__main__':app=QApplication(sys.argv);w=Learnly();w.show();sys.exit(app.exec())