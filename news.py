# from urllib.request import urlopen as urlop
from json import loads
from json import dumps
from urllib.parse import quote
# from time import sleep
# from time import time
# from time import asctime
from os.path import exists
from os import mkdir
# from os import kill
# from signal import SIGTERM
# from os import popen
from os import listdir
from os import remove
# from os import rename
from os import system
from subprocess import run
# from webbrowser import open as webopen
from pathlib import Path
# from pprint import pprint
# from multiprocessing import Process
# from subprocess import check_output
from os.path import abspath
from os.path import dirname
from os import chdir
# from difflib import ndiff
# from shutil import disk_usage
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import unquote as uqu
# from os import getpid
from os.path import exists
from os import remove
# from functools import partial
# from functools import wraps
from base64 import b64encode
from urllib.parse import parse_qs
from err import err
from paths import *
cache='./user_data/.vkfeed/'
from sys import argv
from pprint import pprint

###############################################################################

if not exists(cache):
    mkdir(cache)
# chdir(cache)
if not exists(cache+'post/'):
    mkdir(cache+'post/')
try:
    repo=open(cache+'path').read()
except:
#	repo = str(abspath(dirname(argv[0])))
#	if repo[-1]!='/':
#		repo+='/'
    open(cache+'path','w').write(repo)

try:
    remove(cache+'exit')
except:
    pass

try:
    loads(open(cache+'localstorage').read())
except:
    open(cache+'localstorage','w').write('{}')

###############################################################################

def lp(q):
    print(q)
    return q

# def error():
#     q=format_exc()
#     try:
#         q=q.split('\n')
#         f=q[[e for e,w in enumerate(q) if w.startswith('Traceback')][-1]+1:-2]
#         d=[]
#         while f:
#             d.append('\n'.join(f[:2]))
#             f=f[2:]
#         d=d+[w for w in d if argv[0] in w]
#         d=d[-1]
#         d='line'+d.split('line',1)[1].split('\n')[0]
#         q=d+', '+q[-2]
#         print(q)
#     except:
#         pprint(q,format_exc())

# def err(func):
#     @wraps(func)
#     def run(*q,**w):
#         try:
#             return func(*q,**w)
#         except KeyboardInterrupt:
#             pass
# #			killer()
#         except:
#             error()
#     return run

###############################################################################

@err
def token():
    try:
        return open(cache+'token').read()
    except:
        pass
    input('welcome to vkfeed. you will be redirected to the authorization page, where you need to grant all the permissions required for the application to work. After that, you should copy the url of the page and paste it there.\nPress enter to open the page...')
    try:
        run(['termux-open-url','https://oauth.vk.com/authorize?client_id=7623880&scope=73730&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token&revoke=1'])
    except:
        pass
    print('https://oauth.vk.com/authorize?client_id=7623880&scope=73730&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token&revoke=1')
    url=input('now paste the url: ')
    t=url.split('#')[1].split('&')[0].split('=')[1]
    open(cache+'token','w').write(t)
    return t

token()

###############################################################################

class MyServer(SimpleHTTPRequestHandler):
    @err
    def log_message(*a):
        pass

    @err
    def do_GET(self):
        global cache,repo
        path=self.path
        path=path.split('?')
        path,pathargs=(path+[''])[:2]
        path=uqu(path)
        if path[0]=='/':
            path=path[1:]
        if pathargs==''==path:
            path='index.html'
            print(1)
            print(self.path=='/'+path,self.path,path)
            self.path=path
            super().do_GET()
            return
        pathargs=parse_qs(pathargs)
        if path=='json':
            try:
                db=sorted(listdir(cache+'post/'))[::-1]
            except:
                db=[]
            if len(db)==0:
                db=['00_0']
            db=[{'url':w} for w in db]
            self.send_response(200)
            self.send_header("Content-type", "text/json; charset=utf-8")
            self.end_headers()
            db=dumps(db)
            self.wfile.write(db.encode())
            return
        if path=='post/00_0':
            self.send_response(200)
            self.send_header("Content-type", "file/file")
            self.end_headers()
            self.wfile.write(dumps({'date':'0','public':'vkfeed','orig':'0_0','text':'creating cache...\nconnect to wifi, wait 10 minutes and refresh the page','photos':[]}).encode())
        path=path.split('/')
        if path[0]=='localstorage':
            ls=loads(open(cache+'localstorage').read())
            if path[1]=='set':
                ls[path[2]]=path[3]
                open(cache+'localstorage','w').write(dumps(ls))
                ls='""'
            elif path[1]=='get':
                try:
                    ls=ls[path[2]]
                except:
                    ls=dumps(None)
            self.send_response(200)
            self.send_header("Content-type", "file/file")
            self.end_headers()
            self.wfile.write(ls.encode())
        else:
            super().do_GET()

###############################################################################

if 'cachegen' in argv[1:]:
    token()
    system('python3 "'+repo+'post.py" &')
else:
    print('no new post')

hostPort = 9876

try:
    if 'debug' in argv[1:]:
        myServer = HTTPServer(('0.0.0.0', hostPort), MyServer)
    else:
        myServer = HTTPServer(('127.0.0.1', hostPort), MyServer)
except:
    print('click exit button in termux notification and try agawin')

print("http://127.0.0.1:%s" % (hostPort))
try:
    run(["termux-open-url","http://127.0.0.1:%s" % (hostPort)])
except:
    pass

try:
    myServer.serve_forever()
except KeyboardInterrupt:
    pass


open(cache+'exit','w').write('')
myServer.server_close()
print()
