from kivy.clock import Clock

class CountdownTimer:
    def __init__(self, on_tick=None, on_finished=None):
        self.remaining = 0
        self.event = None
        self.on_tick = on_tick
        self.on_finished = on_finished
    def start(self, seconds):
        self.stop(); self.remaining=max(0,int(seconds)); self._emit(); self.event=Clock.schedule_interval(self._step,1)
    def pause(self):
        if self.event: self.event.cancel(); self.event=None
    def resume(self):
        if self.remaining>0 and not self.event: self.event=Clock.schedule_interval(self._step,1)
    def reset(self, seconds=0):
        self.stop(); self.remaining=max(0,int(seconds)); self._emit()
    def stop(self):
        if self.event: self.event.cancel(); self.event=None
    def _emit(self):
        if self.on_tick: self.on_tick(self.remaining)
    def _step(self, dt):
        self.remaining-=1; self._emit()
        if self.remaining<=0:
            self.stop()
            if self.on_finished: self.on_finished()

class Stopwatch:
    def __init__(self, on_tick=None):
        self.elapsed=0; self.event=None; self.on_tick=on_tick
    def start(self): self.stop(); self.elapsed=0; self._emit(); self.event=Clock.schedule_interval(self._step,1)
    def pause(self):
        if self.event: self.event.cancel(); self.event=None
    def resume(self):
        if not self.event: self.event=Clock.schedule_interval(self._step,1)
    def reset(self): self.stop(); self.elapsed=0; self._emit()
    def _emit(self):
        if self.on_tick: self.on_tick(self.elapsed)
    def _step(self,dt): self.elapsed+=1; self._emit()
