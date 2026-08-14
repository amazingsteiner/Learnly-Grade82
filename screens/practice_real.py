from PySide6.QtWidgets import QLabel,QPushButton,QLineEdit,QComboBox
from .base import Screen
from engine.question_engine import QuestionEngine
from engine.learning.adaptive import AdaptiveEngine
from engine.learning.mastery import MasteryEngine
from engine.session_engine import SessionEngine
import json
from pathlib import Path
class RealPracticeScreen(Screen):
    def __init__(self,app,mode='recommended'):
        super().__init__(app,'Practice'); self.mode=mode; self.qe=QuestionEngine(); self.ad=AdaptiveEngine(app.student); self.me=MasteryEngine(app.student); self.se=SessionEngine(app.student)
        self.add(QLabel('Practice mode')); self.modebox=QComboBox(); self.modebox.addItems(['recommended','weakness','strength','mixed','speed']); self.modebox.currentTextChanged.connect(self.set_mode); self.add(self.modebox)
        self.add(QLabel('Choose topic (optional)')); self.topicbox=QComboBox(); self.topicbox.addItem('Adaptive'); self.topicbox.addItems(self.qe.TOPICS); self.add(self.topicbox)
        self.progress=QLabel(); self.add(self.progress); self.question=QLabel(); self.question.setWordWrap(True); self.question.setStyleSheet('font-size:16pt;font-weight:700;'); self.add(self.question)
        self.answer=QLineEdit(); self.answer.setPlaceholderText('Type your answer'); self.add(self.answer); b=QPushButton('CHECK ANSWER'); b.clicked.connect(self.check); self.add(b); self.hint=QLabel(); self.hint.setWordWrap(True); self.add(self.hint); self.result=QLabel(); self.result.setWordWrap(True); self.add(self.result); n=QPushButton('NEXT QUESTION'); n.clicked.connect(self.next_question); self.add(n); self.next_question()
    def set_mode(self,m): self.mode=m; self.next_question()
    def next_question(self):
        topic=self.topicbox.currentText() if self.topicbox.currentText()!='Adaptive' else self.ad.choose_topic(self.mode); self.q=self.qe.generate(topic,1); self.question.setText(f'{self.q["topic"]}\n\n{self.q["question"]}'); self.hint.setText('💡 '+self.q['hint'] if self.app.student.get('settings',{}).get('hints',True) else ''); self.result.clear(); self.answer.clear(); self.progress.setText(f"Today: {self.app.student.get('today_done',0)} / {self.app.student.get('daily_goal',20)}")
    def check(self):
        if not self.q:return
        u=self.answer.text().strip().lower(); a=self.q['answer'].strip().lower(); correct=u==a; self.se.record(self.q,u,correct); m=self.me.score(self.q['topic'],correct,self.q['difficulty']); self.result.setText(('✓ CORRECT! +10 XP' if correct else f'✗ Answer: {self.q["answer"]}')+f'\n\n{self.q["explanation"]}\n\nMastery: {int(m*100)}%'); p=Path(__file__).resolve().parents[1]/'data'/'students'/f'{self.app.student["code"]}.json'; p.write_text(json.dumps(self.app.student,indent=2,ensure_ascii=False),encoding='utf-8')
