from pathlib import Path
from PySide6.QtWidgets import QMainWindow,QStackedWidget,QMessageBox
from ui.theme_manager import ThemeManager
from screens.login import LoginScreen
from screens.home import HomeScreen
from screens.learn import LearnScreen
from screens.practice_real import RealPracticeScreen
from screens.papers import PapersScreen
from screens.profile import ProfileScreen
from screens.settings import SettingsScreen
from screens.tutor import TutorScreen
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'; STUDENTS=DATA/'students'; ACCESS_CODE='children of the sun'
class LearnlyApp(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle('Learnly — Grade 8 Mathematics'); self.resize(430,760); self.theme=ThemeManager(); self.student=None; self.stack=QStackedWidget(); self.setCentralWidget(self.stack); self.show_login()
    def show_login(self): self.clear(); self.stack.addWidget(LoginScreen(self.login)); self.stack.setCurrentIndex(0)
    def login(self,code):
        code=code.strip().upper()
        if not code: QMessageBox.warning(self,'Login','Enter a student code.'); return
        p=STUDENTS/f'{code}.json'
        if p.exists():
            import json; self.student=json.loads(p.read_text(encoding='utf-8'))
        else:
            self.student={'code':code,'name':f'Student {code}','grade':8,'subject':'Mathematics','term':1,'daily_goal':20,'today_done':0,'streak':0,'xp':0,'mastery':{},'history':[],'settings':{'theme':'Classic Elite','hints':True}}
            p.parent.mkdir(parents=True,exist_ok=True); import json; p.write_text(json.dumps(self.student,indent=2),encoding='utf-8')
        self.student['grade']=8; self.student['subject']='Mathematics'; self.theme.set_theme(self.student.get('settings',{}).get('theme','Classic Elite')); self.show_home()
    def clear(self):
        while self.stack.count(): w=self.stack.widget(0); self.stack.removeWidget(w); w.deleteLater()
    def navigate(self,name):
        screens={'home':HomeScreen,'learn':LearnScreen,'practice':lambda a:RealPracticeScreen(a,'recommended'),'papers':PapersScreen,'profile':ProfileScreen,'settings':SettingsScreen,'tutor':TutorScreen}; cls=screens[name]; self.clear(); self.stack.addWidget(cls(self)); self.stack.setCurrentIndex(0)
    def show_home(self): self.navigate('home')
    def show_learn(self): self.navigate('learn')
    def show_practice(self): self.navigate('practice')
    def show_papers(self): self.navigate('papers')
    def show_profile(self): self.navigate('profile')
    def show_settings(self): self.navigate('settings')
    def show_tutor(self): self.navigate('tutor')
