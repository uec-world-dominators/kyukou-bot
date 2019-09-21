

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

    def set_progress(self, id, progress):
        self.collection[id] = progress

    def get_progress(self, id):
        progress = self.collection.get(id)
        return -1 if progress == None else progress

    def run(self, id, *args):
        if self.get_progress(id)+1 >= len(self.processes):
            raise RuntimeError
        else:
            r = self.processes[self.get_progress(id)+1]["func"](id, *args)
            if self.get_progress(id) == len(self.processes)-1:
                self.set_progress(id, -1)
            return r

    def check(self, id, *args):
        if self.oncondition(id, *args):
            self.set_progress(id, -1)
            return True
        else:
            return len(self.processes) > self.get_progress(id) > -1

    def end(self, id):
        self.set_progress(id, -1)


class ProcedureSelector():
    def __init__(self, procedures):
        self.procedures = procedures
        self.current = {}

    def run(self, id, *args):
        if self.current.get(id) and self.procedures[self.current[id]].check(id, *args):
            return True
        for i, procedure in enumerate(self.procedures):
            if procedure.check(id, *args):
                procedure.run(id, *args)
                self.current[id] = i
                return True
        return None

    def end(self, id):
        for procedure in self.procedures:
            procedure.end(id)


if __name__ == '__main__':
    p = Procedure(lambda id, *args: args[0] == 'mail')
    @process(p, 0)
    def process0(id, args):
        print('0', id)
        p.set_progress(id, 0)

    @process(p, 1)
    def process1(id, args):
        print('1', id)
        p.set_progress(id, 1)

    p2 = Procedure(lambda id, *args: args[0] == 'csv')

    @process(p2, 0)
    def process20(id, args):
        print('p2', id)
        p2.set_progress(id, 0)

    ps = ProcedureSelector([p, p2])
    args = ['mail']
    ps.run('hoge', *args)
    ps.run('hige', *args)
    args = ['mail']
    ps.run('hige', *args)
    args = ['me@shosato.jp']
    ps.run('hoge', *args)

__all__ = ["Procedure", "process", "ProcedureSelector"]
