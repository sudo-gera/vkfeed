''':'
python3 $0 $@
exit
':'''

###############################################################################

from urllib.request import urlopen as urlop
from json import loads
from json import dumps
from urllib.parse import quote
from time import sleep
from time import time
from time import asctime
from traceback import format_exc
from os.path import exists
from os import mkdir
from os import kill
from signal import SIGTERM
from os import popen
from os import listdir
from os import remove
from os import rename
from os import system
from subprocess import run
from webbrowser import open as webopen
from sys import argv
from pathlib import Path
from pprint import pprint
from multiprocessing import Process
from subprocess import check_output
from os.path import abspath
from os.path import dirname
from os import chdir
from difflib import ndiff
from shutil import disk_usage
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote as uqu
from os import getpid
from os.path import exists
from os import remove
from functools import partial
from functools import wraps
from base64 import b64encode

###############################################################################

home=str(Path.home())+'/'
cache=home+'.vkfeed/'
if not exists(cache):
	mkdir(cache)
chdir(cache)
if not exists('post/'):
	mkdir('post/')
try:
	repo=open('path').read()
except:
	repo = str(abspath(dirname(argv[0])))
	if repo[-1]!='/':
		repo+='/'
	open('path','w').write(repo)

###############################################################################

def lp(q):
	print(q)
	return q

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
			killer()
		except:
			error()
	return run

###############################################################################

class MyServer(BaseHTTPRequestHandler):
	@err
	def log_message(*a):
		pass

	@err
	def do_GET(self):
		global cache,repo
		path=self.path
		path=uqu(path)
		if path[0]=='/':
			path=path[1:]
		if path=='':
			path='index.html'
			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.end_headers()
			self.wfile.write(open(repo+path,'rb').read())
			return
		if path=='kill':
			process(stopserver,nokill=1)
		if path=='json':
			try:
				db=sorted(listdir('post/'))[::-1]
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
		if len(path)==1:
			path=[repo]+path
		if len(path)==2 and path[0] in [repo,'post']:
			post=0
			if path[0]=='post':
				post=1
			path='/'.join(path)
			if exists(path):
				self.send_response(200)
				self.send_header("Content-type", "file/file")
				self.end_headers()
				file=open(path,'rb').read()
				if post:
					file=bytearray(file)
					file=file.split('\0'.encode(),1)
					j=loads(file[0].decode())
					p=j['photos']
					w=0
					while w!=len(p):
						p[w]=file[1][p[w]:p[w+1] if w+1<len(p) else len(file[1])]
						w+=1
					p=[b64encode(w).decode() for w in p]
					j['photos']=p
					file=dumps(j)
					file=file.encode()
				self.wfile.write(file)
			else:
				self.send_response(404)
				self.send_header("Content-type", "file/file")
				self.end_headers()

###############################################################################

system('python3 "'+path+'post.py" &')

hostPort = 9876

try:
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

open('exit').write('')
myServer.server_close()
print()