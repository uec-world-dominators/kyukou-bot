import time
from .db import get_collection
import random
from pprint import pprint
from .scheduler import add_task


def process(p, n):
    def wrapper(f):
        p.processes.append({
            "order": n,
            "func": f
        })

        def _wrapper():
            f(n)
        return _wrapper
    return wrapper


class Procedure():
    def __init__(self, oncondition):
        self.collection = {}
        self.processes = []
        self.oncondition = oncondition

    def set_progress(self, _id, progress):
        self.collection[_id] = progress

    def get_progress(self, _id):
        progress = self.collection.get(_id)
        return -1 if progress == None else progress

    def run(self, _id, *args):
        if self.get_progress(_id)+1 >= len(self.processes):
            raise RuntimeError
        else:
            r = self.processes[self.get_progress(_id)+1]["func"](_id, *args)
            if self.get_progress(_id) == len(self.processes)-1:
                self.remove(_id)
            return r

    def check(self, _id, *args):
        if self.oncondition(_id, *args):
            return True
        else:
            return len(self.processes) > self.get_progress(_id) > -1

    def end(self, _id):
        self.remove(_id)

    def remove(self, _id):
        del self.collection['_id']


class ProcedureDB(Procedure):
    def __init__(self, oncondition, procedure_id, timeout=3600):
        self.collection = get_collection('procedure')
        self.processes = []
        self.oncondition = oncondition
        self.procedure_id = procedure_id
        self.timeout = timeout
        add_task(60, self.clear)

    def set_progress(self, _id, progress):
        if not self.collection.update_one({'id': _id, 'procedure_id': self.procedure_id}, {
                '$set': {
                    'progress': progress
                }}).matched_count:
            self.collection.insert_one({'id': _id, 'procedure_id': self.procedure_id,
                                        'progress': progress,
                                        'expired_at': time.time()+self.timeout})

    def get_progress(self, _id):
        r = self.collection.find_one({'id': _id, 'procedure_id': self.procedure_id})
        return -1 if r == None else r.get('progress')

    def clear(self):
        self.collection.delete_many({'procedure_id': self.procedure_id,
                                     'expired_at': {'$lt': time.time()}})
        self.collection.delete_many({'progress': -1})

    def remove(self, _id):
        self.collection.delete_one({'id': _id, 'procedure_id': self.procedure_id})


class ProcedureSelector():
    def __init__(self, *procedures):
        self.procedures = procedures
        self.current = {}

    def run(self, _id, *args):
        if self.current.get(_id) and self.procedures[self.current[_id]].check(_id, *args):
            return True
        for i, procedure in enumerate(self.procedures):
            if procedure.check(_id, *args):
                procedure.run(_id, *args)
                self.current[_id] = i
                return True
        return None

    def end(self, _id):
        for procedure in self.procedures:
            procedure.end(_id)

    def clear(self):
        for procedure in self.procedures:
            if hasattr(procedure, 'clear'):
                procedure.clear()


if __name__ == '__main__':
    p = ProcedureDB(lambda id, *args: args[0] == 'mail')
    @process(p, 0)
    def process0(id, args):
        print('0', id)
        p.set_progress(id, 0)

    @process(p, 1)
    def process1(id, args):
        print('1', id)
        p.set_progress(id, 1)

    p2 = ProcedureDB(lambda id, *args: args[0] == 'csv')

    @process(p2, 0)
    def process20(id, args):
        print('p2', id)
        p2.set_progress(id, 0)

    ps = ProcedureSelector(p, p2)
    args = ['mail']
    ps.run('hoge', *args)
    ps.run('hige', *args)
    args = ['mail']
    ps.run('hige', *args)
    args = ['me@shosato.jp']
    ps.run('hoge', *args)

__all__ = ["Procedure", "ProcedureDB", "process", "ProcedureSelector"]
