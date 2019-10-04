from datetime import datetime
isinpackage = not __name__ in ['info', '__main__']
if isinpackage:
    from .db import get_collection
else:
    from db import get_collection

datetime.fromtimestamp(2).strftime("%Y/%m/%d")


def create_md():
    md = '# 過去の休講情報一覧\n\n'
    md += '|日付|時限|教科|教員|備考|\n'
    md += '|---|---|---|---|---|\n'
    lectures = get_collection('lectures')
    for lecture in lectures.find({}):
        md += f'|{datetime.fromtimestamp(lecture.get("date")).strftime("%Y/%m/%d")}|{"・".join(map(str,lecture.get("periods")))}|{lecture.get("subject")}|{lecture.get("teachers")}|{lecture.get("remark")}|\n'

    with open('web/public/lectures.md', 'wt', encoding='utf-8') as f:
        f.write(md)
create_md()