from dataclasses import dataclass
@dataclass
class Shape:
    kind:str
    points:list
    label:str=""
class GeometryEngine:
    def triangle(self,a,b,c,label=""): return Shape("triangle",[a,b,c],label)
    def rectangle(self,x,y,w,h,label=""): return Shape("rectangle",[(x,y),(x+w,y),(x+w,y+h),(x,y+h)],label)
    def circle(self,center,radius,label=""): return Shape("circle",[center,radius],label)
