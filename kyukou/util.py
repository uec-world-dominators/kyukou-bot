import random
import inspect


def dict_to_tuples(d):
    return [(key, value) for key, value in d.items()]


id_string = 'abcdefghijklmnopqrstuvwxyz0123456789'


def generate_id(n):
    return ''.join([random.choice(id_string) for i in range(n)])


class Just(object):
    """
    # Maybe Monad
    ## usage
    ```
    d = {
        "a": {
            "b": 1
        }
    }
    ```
    ### Get Value from Maybe Monad
    ```
    Just(d).a() # {'b': 1}
    Just(d).a.b() # 1
    Just(d).a.b.c() # None
    ```
    ### None Propagation
    ```
    Just(d).b.c() # None
    ```
    ### Default Value
    ```
    Just(d).b.c('Default') # 'Default'
    ```
    ### Function
    ```
    Just(d).a.b[lambda n:n*10]() # 10
    ```
    """

    def __init__(self, a):
        object.__setattr__(self, 'a', a)

    def __call__(self, default=None):
        a = object.__getattribute__(self, 'a')
        return default if a == None else a

    def __getattribute__(self, key):
        a = object.__getattribute__(self, 'a')
        if isinstance(a, dict) and (key in a):
            return Just(a[key])
        else:
            return Just(None)

    def __getitem__(self, f):
        if callable(f):
            return Just(f(object.__getattribute__(self, 'a')))
        elif isinstance(f, str):
            return object.__getattribute__(self, 'a')[f]  # 既存コードとの互換性のためJustは返さない
        else:
            raise RuntimeError

    def __rshift__(self, f):
        if callable(f):
            return Just(f(object.__getattribute__(self, 'a')))


class Curry(object):
    """
    # Curry
    ```
    def f(a, b):
        return a+b
    print(Just([1, 2, 3])[Curry(map, 2)[lambda n:n**2]][list][sum]())
    # 14
    ```
    """

    def __init__(self, f, argc=None):
        self.f = f
        self.argv = []
        self.argc = argc or len(inspect.getfullargspec(f).args)

    def __getitem__(self, x):
        if isinstance(x, tuple):
            self.argv += list(x)
        else:
            self.argv.append(x)
        if len(self.argv) > self.argc:
            raise RuntimeError
        return self

    def __call__(self, *args):
        if len(self.argv)+len(args) != self.argc:
            raise RuntimeError
        else:
            return self.f(*self.argv, *args)

process=[]

def procedure(n):
    def wrapper(f):
        process.append({
            "order": n,
            "func": f
        })

        def _wrapper():
            f(n)
        return _wrapper
    return wrapper


class Procedure():
    # process = []

    def __init__(self, collection={}):
        self.collection = collection

    def set_progress(self, id, progress):
        self.collection[id] = progress

    def get_progress(self, id):
        return self.collection[id] or 0

    def run(self, id, *args):
        if self.get_progress(id)+1 >= len(process):
            return None
        else:
            return process[self.get_progress(id)+1](*args)

    @procedure(0)
    def start_mail_setting(self, id, args):
        self.set_progress(id, 0)
        print('0 '+id)
        return 'write mail'

    @procedure(1)
    def validate_mail(self, id, args):
        print('1 '+id)
        if args:
            self.set_progress(id, 1)
        else:
            self.set_progress(id, 0)


if __name__ == '__main__':
    p = Procedure()
    p.run('hoge', True)
    p.run('hoge', True)


__all__ = ["dict_to_tuples", "generate_id", "Just", "Curry"]

# class AttrDict(object):
#     """
#     # AttrDict Class
#     ## allow attrubute access for dict

#     ```
#     d = {
#         "a": {
#             "b": 1
#         }
#     }
#     ad = AttrDict(d)
#     print(ad.a) # <AttrDict object>
#     print(ad.a.b) # 1
#     ```
#     """

#     def __init__(self, d):
#         object.__setattr__(self, '__dict__', d)
#         for k in d.keys():
#             if isinstance(d[k], dict):
#                 d[k] = AttrDict(d[k])

#     def __getitem__(self, key):
#         if isinstance(key, tuple):
#             return get_nested_item(object.__getattribute__(self, '__dict__'), key[0], None)
#         else:
#             return get_nested_item(object.__getattribute__(self, '__dict__'), key, None)

#     def __contains__(self, key):
#         return key in object.__getattribute__(self, '__dict__')

#     def __getattribute__(self, key):
#         return get_nested_item(object.__getattribute__(self, '__dict__'), key, None)

#     def get(self, key):
#         return object.__getattribute__(self, '__dict__').get(key)

#     def todict(self):
#         return object.__getattribute__(self, '__dict__')


# def get_nested_item_basic(d, keys, default=None):
#     if not (isinstance(d, dict) or isinstance(d, AttrDict)) or not keys[0] in d:
#         return default
#     if len(keys) == 1:
#         return d[keys[0]]
#     else:
#         return get_nested_item_basic(d[keys[0]], keys[1:], default)


# def get_nested_item(d, keys_src, default=None):
#     return get_nested_item_basic(d, keys_src.split('.'), default)
