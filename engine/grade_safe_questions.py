import random

class GradeSafeQuestion:
    def generate(self, grade, topic, difficulty=2):
        g = int(grade.split()[-1]) if grade != "Grade R" else 0
        if g >= 8:
            return None
        if topic in {"counting","whole_numbers"}:
            if g <= 1: a,b=random.randint(1,20),random.randint(1,20); return self._q(topic,f"Count: {a}, {a+1}, {a+2}, __",a+3)
            a,b=random.randint(10,99),random.randint(1,30); return self._q(topic,f"Calculate: {a} + {b}",a+b)
        if topic in {"addition_subtraction","multiplication_division"}:
            if topic=="addition_subtraction":
                a,b=random.randint(1,100),random.randint(1,50); return self._q(topic,f"Calculate: {a} − {b}",a-b)
            b=random.randint(2,10); a=b*random.randint(2,12); return self._q(topic,f"Calculate: {a} ÷ {b}",a//b)
        if topic=="fractions":
            d=random.choice([2,3,4,5,10]); n=random.randint(1,d-1); return self._q(topic,f"What fraction is {n} out of {d}?",f"{n}/{d}")
        if topic=="decimals":
            a=round(random.randint(10,99)/10,1); b=round(random.randint(10,99)/10,1); return self._q(topic,f"Calculate: {a} + {b}",round(a+b,1))
        if topic=="percentages":
            p=random.choice([10,20,25,50]); n=random.choice([40,60,80,100,200]); return self._q(topic,f"Find {p}% of {n}.",n*p//100)
        if topic in {"factors_multiples","ratio_rate"}:
            a=random.randint(2,12); return self._q(topic,f"Give a multiple of {a} between 10 and 60.",a*random.randint(2,5))
        if topic in {"patterns","algebra_patterns"}:
            start=random.randint(1,10); step=random.randint(2,6); return self._q(topic,f"Find the next term: {start}, {start+step}, {start+2*step}, __",start+3*step)
        if topic=="integers":
            a=random.randint(-12,12); b=random.randint(-12,12); return self._q(topic,f"Calculate: {a} + ({b})",a+b)
        if topic in {"geometry","geometry_lines","shapes"}:
            return self._q(topic,"How many degrees are in a right angle?",90)
        if topic=="measurement":
            return self._q(topic,"How many centimetres are in 1 metre?",100)
        if topic in {"data","data_handling"}:
            a,b,c=2,4,6; return self._q(topic,"Find the mean of 2, 4 and 6.",4)
        if topic=="probability": return self._q(topic,"A fair coin is tossed. What is P(heads)?","1/2")
        return self._q(topic,"What is 2 + 2?",4)
    def _q(self,topic,question,answer):
        return {"id":f"safe_{random.randint(100000,999999)}","topic":topic,"topic_name":topic.replace('_',' ').title(),"question":question,"answer":str(answer),"difficulty":2,"marks":1,"hint":"Use the basic rule for this topic.","explanation":f"The answer is {answer}."}
