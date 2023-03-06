from traceback import format_exc
from functools import wraps
from pprint import pprint
from sys import argv
def error():
    q=format_exc()
    try:
        q=q.split('\n')
        f=q[[e for e,w in enumerate(q) if w.startswith('Traceback')][-1]+1:-2]
        d=[]
        while f:
            d.append('\n'.join(f[:2]))
            f=f[2:]
        d=d+[w for w in d if argv[0] in w]
        d=d[-1]
        d='line'+d.split('line',1)[1].split('\n')[0]
        q=d+', '+q[-2]
        print(q)
    except:
        pprint(q,format_exc())

def err(func):
    @wraps(func)
    def run(*q,**w):
        try:
            return func(*q,**w)
        except KeyboardInterrupt:
            pass
        except:
            error()
    return run

