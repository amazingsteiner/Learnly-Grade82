from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from .question_engine import QuestionEngine
from .grade_safe_questions import GradeSafeQuestion


def font(size):
    candidates=["/system/fonts/Roboto-Regular.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for p in candidates:
        if Path(p).exists(): return ImageFont.truetype(p,size)
    return ImageFont.load_default()


def make_paper(student, topic=None, count=10):
    root=Path(__import__('kivy').app.App.get_running_app().user_data_dir)
    out=root/"Pictures"/"Learnly"; out.mkdir(parents=True,exist_ok=True)
    grade=student.get("grade","Grade 8"); qe=QuestionEngine(); safe=GradeSafeQuestion(); questions=[]
    for i in range(count):
        tid=topic
        if not tid:
            allowed=__import__('json').loads((Path(__file__).resolve().parents[1]/"content/curriculum/grade_map.json").read_text())["grades"][grade]["topic_ids"]
            tid=allowed[i%len(allowed)]
        try:
            q=qe.generate(tid,2) if grade in ("Grade 8","Grade 9") else safe.generate(grade,tid,2)
        except Exception:
            q=safe.generate(grade,tid,2)
        if q: questions.append(q)
    w,h=1654,2339; img=Image.new("RGB",(w,h),"white"); draw=ImageDraw.Draw(img)
    title=font(54); head=font(32); body=font(28); small=font(22)
    draw.text((90,70),"LEARNLY MATHEMATICS",font=title,fill="black")
    draw.text((90,145),f"{grade} • {topic.replace('_',' ').title() if topic else 'Mixed'}",font=head,fill="black")
    draw.text((90,205),f"Name: ____________________________    Date: ______________",font=small,fill="black")
    y=280
    for i,q in enumerate(questions,1):
        text=f"{i}. {q['question']}"
        for line in text.split("\n"):
            draw.text((100,y),line,font=body,fill="black"); y+=42
        draw.line((100,y+28,1500,y+28),fill="black",width=2); y+=70
        if y>2180: break
    path=out/f"Learnly_{grade.replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"; img.save(path)
    return str(path)
