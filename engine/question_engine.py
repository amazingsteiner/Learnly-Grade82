import random, math

class QuestionEngine:
    TOPICS = [
        'Whole Numbers','Integers','Exponents','Numeric Patterns',
        'Algebraic Expressions','Algebraic Equations','Geometry of Straight Lines',
        'Pythagoras','Area & Perimeter','Financial Mathematics',
        'Transformations','Data Handling','Probability','Mental Maths'
    ]
    def generate(self, topic=None, difficulty=1):
        topic = topic or random.choice(self.TOPICS)
        fn = getattr(self, '_' + topic.lower().replace(' & ','_').replace(' ','_'), None)
        return fn(difficulty) if fn else self._mental_maths(difficulty)
    def _base(self,t,q,a,d,h,e):
        return {'id':f'{t}_{random.randint(100000,999999)}','topic':t,'question':q,
                'answer':str(a),'difficulty':d,'hint':h,'explanation':e,'marks':max(1,d)}
    def _whole_numbers(self,d):
        a=random.randint(100,9999); b=random.randint(10,999)
        return self._base('Whole Numbers',f'Calculate: {a} + {b}',a+b,d,'Add from right to left.',f'{a}+{b}={a+b}.')
    def _integers(self,d):
        a=random.randint(-30,30); b=random.randint(-20,20)
        return self._base('Integers',f'Calculate: {a} - ({b})',a-b,d,'Subtracting a negative adds.',f'{a}-{b}={a-b}.')
    def _exponents(self,d):
        a=random.randint(2,5); x=random.randint(1,3+d); y=random.randint(1,3+d)
        return self._base('Exponents',f'Simplify: {a}^{x} × {a}^{y}',f'{a}^{x+y}',d,'Same base: add exponents.',f'{a}^{x}×{a}^{y}={a}^{x+y}.')
    def _numeric_patterns(self,d):
        a=random.randint(1,20); step=random.randint(2,12); n=random.randint(4,7); seq=[a+i*step for i in range(n)]
        return self._base('Numeric Patterns',f'Find the next term: {", ".join(map(str,seq))}, ?',seq[-1]+step,d,'Find the constant difference.',f'Each term increases by {step}.')
    def _algebraic_expressions(self,d):
        a=random.randint(2,12); b=random.randint(2,12)
        return self._base('Algebraic Expressions',f'Simplify: {a}x + {b}x',f'{a+b}x',d,'Collect like terms.',f'{a}x+{b}x={a+b}x.')
    def _algebraic_equations(self,d):
        a=random.randint(2,9); x=random.randint(2,15); b=random.randint(1,15); c=a*x+b
        return self._base('Algebraic Equations',f'Solve: {a}x + {b} = {c}',x,d,'Undo addition, then divide.',f'{a}x={c-b}, so x={x}.')
    def _geometry_of_straight_lines(self,d):
        a=random.randint(30,150); ans=180-a
        return self._base('Geometry of Straight Lines',f'Angles on a straight line: {a}° + x = 180°. Find x.',f'{ans}°',d,'Angles on a straight line total 180°.',f'x=180-{a}={ans}°.')
    def _pythagoras(self,d):
        pairs=[(3,4,5),(5,12,13),(6,8,10),(8,15,17)]; x,y,h=random.choice(pairs)
        return self._base('Pythagoras',f'A right triangle has legs {x} and {y}. Find the hypotenuse.',h,d,'Use a²+b²=c².',f'c=√({x}²+{y}²)={h}.')
    def _area_perimeter(self,d):
        w=random.randint(3,15); h=random.randint(3,15)
        return self._base('Area & Perimeter',f'Find the area of a rectangle {w} units by {h} units.',w*h,d,'Area = length × width.',f'{w}×{h}={w*h} square units.')
    def _financial_mathematics(self,d):
        p=random.randint(100,2000); r=random.choice([5,10,15]); t=random.randint(1,3); interest=p*r*t/100
        ans=f'{interest:.2f}'
        return self._base('Financial Mathematics',f'Find simple interest on R{p} at {r}% p.a. for {t} year(s).',ans,d,'I = PRT/100.',f'I={p}×{r}×{t}/100=R{ans}.')
    def _transformations(self,d):
        x=random.randint(-5,5); y=random.randint(-5,5)
        return self._base('Transformations',f'Reflect ({x}, {y}) in the x-axis. Give the image coordinate.',f'({x}, {-y})',d,'Reflection in x-axis changes the sign of y.',f'({x},{y})→({x},{-y}).')
    def _data_handling(self,d):
        vals=[random.randint(1,20) for _ in range(5)]; mean=sum(vals)/len(vals)
        ans=f'{mean:g}'
        return self._base('Data Handling',f'Find the mean of: {", ".join(map(str,vals))}',ans,d,'Add all values and divide by the number of values.',f'Sum={sum(vals)}, count=5, mean={ans}.')
    def _probability(self,d):
        red=random.randint(1,5); blue=random.randint(1,5); total=red+blue; g=math.gcd(red,total)
        return self._base('Probability',f'A bag has {red} red and {blue} blue counters. P(red)=?',f'{red//g}/{total//g}',d,'Favourable outcomes ÷ total outcomes.',f'{red}/{total} simplifies to {red//g}/{total//g}.')
    def _mental_maths(self,d):
        a=random.randint(10,80)
        return self._base('Mental Maths',f'Calculate mentally: {a} × 25',a*25,d,'×25 = ×100 ÷4.',f'{a}×25={a*100}÷4={a*25}.')
