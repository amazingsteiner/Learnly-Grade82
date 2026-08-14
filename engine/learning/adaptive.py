import random
class AdaptiveEngine:
    def __init__(self,student):
        self.student=student; self.mastery=student.setdefault('mastery',{})
    def choose_topic(self,mode='recommended'):
        topics=['Whole Numbers','Integers','Exponents','Numeric Patterns','Algebraic Expressions','Algebraic Equations','Geometry of Straight Lines','Pythagoras','Area & Perimeter','Financial Mathematics','Transformations','Data Handling','Probability','Mental Maths']
        for t in topics: self.mastery.setdefault(t,.5)
        items=list(self.mastery.items())
        if mode in ('weakness','recommended'): return min(items,key=lambda x:x[1])[0]
        if mode=='strength': return max(items,key=lambda x:x[1])[0]
        if mode=='mixed': return random.choice(items)[0]
        if mode=='speed': return random.choice(['Mental Maths','Whole Numbers','Integers','Exponents'])[0]
        return random.choice(topics)
