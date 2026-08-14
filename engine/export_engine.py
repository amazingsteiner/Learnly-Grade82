import json
from datetime import datetime
from pathlib import Path
class ExportEngine:
    def __init__(self,root): self.root=Path(root)
    def export_student(self,student):
        p=self.root/"data"/"exports"/f"{student['code']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps({"format":"learnly_student_export_v1","exported_at":datetime.now().isoformat(),"student":student},indent=2,ensure_ascii=False),encoding="utf-8")
        return p
