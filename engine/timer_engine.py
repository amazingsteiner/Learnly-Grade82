from PySide6.QtCore import QTimer,Signal,QObject
class CountdownTimer(QObject):
    tick=Signal(int); finished=Signal()
    def __init__(self,parent=None):
        super().__init__(parent); self.timer=QTimer(self); self.timer.timeout.connect(self._step); self.remaining=0
    def start(self,seconds):
        self.remaining=max(0,int(seconds)); self.tick.emit(self.remaining); self.timer.start(1000)
    def stop(self): self.timer.stop()
    def _step(self):
        self.remaining-=1; self.tick.emit(max(0,self.remaining))
        if self.remaining<=0: self.timer.stop(); self.finished.emit()
