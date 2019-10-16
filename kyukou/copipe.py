import re
import sys
import codecs
from pprint import pprint
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

NOT_REGISTERED = '未登録'


def load(src: str) -> [object]:
    try:
        return concat(load_basic(src))
    except:
        return None


def load_basic(src: str) -> [object]:
    temp = []
    in_data = False
    dayofweek = 0
    period = 0
    line_gen = (x for x in src.split('\n'))
    for line in line_gen:
        line = line.strip()
        m = re.match(r'(\d)限', line)
        if m:
            in_data = True
            dayofweek = 0
            period += 1
        elif line == NOT_REGISTERED:
            dayofweek += 1
        elif line == '':
            if in_data:
                break
        else:
            if in_data:
                class_num = line
                subject = next(line_gen).strip()
                teachers = next(line_gen).strip()
                temp.append({
                    'periods': [period],
                    'dayofweek': dayofweek,
                    'class_num': class_num,
                    'subject': subject,
                    'teachers': teachers
                })
            dayofweek += 1

    return temp


def concat(temp: [object]) -> [object]:
    '''
    同じ曜日で連続する時限をくっつける
    '''
    temp.sort(key=lambda e: e['dayofweek'])
    result = []
    last = None
    for e in temp:
        if last and last['dayofweek'] == e['dayofweek'] and last['subject'] == e['subject']:
            last['periods'].append(e['periods'][0])
        else:
            result.append(e)
            last = e
    return result
