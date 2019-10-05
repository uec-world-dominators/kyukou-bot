from datetime import datetime
isinpackage = not __name__ in ['info', '__main__']
if isinpackage:
    from .db import get_collection
else:
    from db import get_collection


def create_md():
    md = '# 過去の休講情報一覧\n\n'
    md += '最終更新\\: '+datetime.now().strftime("%Y年%m月%d日 %H時%M分%S秒")+'\n\n'
    md += '|日付|時限|時間割コード|対象|教科|教員|備考|\n'
    md += '|---|---|---|---|---|---|---|\n'
    lectures = get_collection('lectures')
    for lecture in lectures.find({}):
        md += f'|{datetime.fromtimestamp(lecture.get("date")).strftime("%Y/%m/%d")}|{", ".join(map(str,lecture.get("periods")))}|{lecture.get("class_num","不明")}|{lecture.get("class","-")}|{lecture.get("subject")}|{lecture.get("teachers")}|{lecture.get("remark","なし") or "-"}|\n'
    with open('web/public/lectures.md', 'wt', encoding='utf-8') as f:
        f.write(md)


if not isinpackage:
    create_md()
