isinpackage = not __name__ in ['info', '__main__']
if isinpackage:
    from .db import get_collection
else:
    from db import get_collection

def syllabus_links(realid):
    pass