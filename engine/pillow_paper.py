from pathlib import Path
from datetime import datetime
import json
from PIL import Image, ImageDraw, ImageFont
from .question_engine import QuestionEngine
from .grade_safe_questions import GradeSafeQuestion

ROOT=Path(__file__).resolve().parents[1]

def font(size):
    candidates=['/system/fonts/Roboto-Regular.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']
    for p in candidates:
        if Path(p).exists(): return ImageFont.truetype(p,size)
    return ImageFont.load_default()

def make_paper(student,topic=None,count=10):
    out=ROOT/'data'/'papers';out.mkdir(parents=True,exist_ok=True)
    grade=student.get('grade','Grade 8'); safe=GradeSafeQuestion(); qe=QuestionEngine(); questions=[]
    grade_map=json.loads((ROOT/'content'/'curriculum'/'grade_map.json').read_text(encoding='utf-8'))
    allowed=grade_map['grades'].get(grade,{}).get('topic_ids',[])
    if topic and topic not in allowed: raise ValueError('Topic is not allowed for this grade.')
    for i in range(count):
        tid=topic or allowed[i%len(allowed)]
        try:q=qe.generate(tid,2) if grade in ('Grade 8','Grade 9') else safe.generate(grade,tid,2)
        except Exception:q=safe.generate(grade,tid,2)
        if q:questions.append(q)
    w,h=1654,2339;img=Image.new('RGB',(w,h),'white');draw=ImageDraw.Draw(img);title=font(52);head=font(30);body=font(27);small=font(21)
    draw.text((90,60),'LEARNLY MATHEMATICS',font=title,fill='black');draw.text((90,130),f'{grade} • {topic.replace("_"," ").title() if topic else "Mixed"}',font=head,fill='black');draw.text((90,190),'Name: ____________________________    Date: ______________',font=small,fill='black')
    y=260
    for i,q in enumerate(questions,1):
        for line in str(q['question']).split('\n'):
            draw.text((100,y),f'{i}. {line}' if line==str(q['question']).split('\n')[0] else line,font=body,fill='black');y+=42
        draw.line((100,y+20,1500,y+20),fill='black',width=2);y+=65
        if y>2200:break
    path=out/f"Learnly_{grade.replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png";img.save(path);return str(path)
