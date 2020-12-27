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
open('post/00_0','w').write(dumps({'date':'0','public':'vkfeed','orig':'0_0','text':'creating cache...\nconnect to wifi, wait 10 minutes and refresh the page','photos':[]}))
try:
	repo=open('path').read()
except:
	repo = str(abspath(dirname(argv[0])))
	if repo[-1]!='/':
		repo+='/'
	open('path','w').write(repo)

open('pid','w').write(str(getpid())+'\n')
open('end','w').write('')

###############################################################################

def lprint(q):
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
	run.f_n=func.__name__
	return run

def serverkill():
	urlop("http://127.0.0.1:%s/kill" % (hostPort)).read()

def killer():
	process(killprocess,nokill=1)

def killprocess():
	print('killing')
	serverkill()
	myServer.server_close()
	p=str(getpid())
	pid=open('pid').read().split('\n')
	end=open('end').read().split('\n')
	for w in pid:
		if w != p and w not in end:
			try:
				kill(int(w),SIGTERM)
			except:
				pass
	sleep(0.7)
	print('killed')
	print()
	exit()

###############################################################################

@err
def process(p,a=(),nokill=0,force=1):
	def run(*q,**w):
		if nokill==0:
			open('pid','a').write(str(getpid())+'\n')
		try:
			p(*q,**w)
		except KeyboardInterrupt:
			killer()
		except:
			error()
		if nokill==0:
			open('end','a').write(str(getpid())+'\n')
	if force==0:
		while not sysfree():
			delay=2+0.25*(len(open('pid').read().split('\n'))-len(open('end').read().split('\n')))
			sleep(delay)
	d=Process(target=run,args=a)
	d.start()

###############################################################################

@err
def service(func):
	try:
		d=loads(open('service_db.json').read())
	except:
		d={}
	try:
		n=func.f_n
	except:
		n=__name__
	d[n]={}
	open('service_db.json','w').write(dumps(d))
	return func

@err
def service_run():
	while 1:
		try:
			d=loads(open('service_db.json').read())
		except:
			d={}
		for w in d.keys():
			try:
				eval(w)(d[w])
			except:
				error()
		open('service_db.json','w').write(dumps(d))
		sleep(64)

@err
def service_get(n):
	try:
		d=loads(open('service_db.json').read())
	except:
		d={}
	try:
		return d[n][n]
	except:
		return None

@err
def service_wait(n):
	while not service_get(n):
		sleep(1)

open('service_db.json','w').write(dumps({}))

###############################################################################

@err
def get_db():
	try:
		db=sorted(listdir('post/'))[::-1]
	except:
		db=[]
	return db

###############################################################################

@err
def token():
	try:
		return vk_token
	except:
		pass
	try:
		return open('token').read()
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
	open('token','w').write(t)
	return t

@err
def urlopen(*q,**w):
	service_wait('wifi')
	return urlop(*q,**w)

@err
def items(q):
	if type(q) == type(dict()):
		if set(q.keys()) == set(['count', 'items']):
			return items(q['items'])
		else:
			for w in q:
				q[w] = items(q[w])
			return q
	elif type(q) == type(list()):
		return [items(w) for w in q]
	else:
		return q

@err
def api(path,data=''):
	if path and path[-1] not in '&?':
		if '?' in path:
			path+='&'
		else:
			path+='?'
	sleep(1/6)
	data=data.encode()
	ret= loads(urlopen('https://api.vk.com/method/'+path+'v=5.101&access_token='+token(),data=data).read().decode())
	try:
		return items(ret['response'])
	except:
		pass
	try:
		print(ret['error']['error_msg'])
	except:
		pprint(ret)

###############################################################################

@service
@err
def monitor(d):
	db=get_db()
	if 'all' in d:
		news=len([w for w in db if w not in d['all']])
		dels=len([w for w in d['all'] if w not in db])
		print(asctime()+'; new downloaded: '+str(news)+'; old deleted: '+str(dels)+'; total posts: '+str(len(db))+'\n')
	else:
		print(asctime()+'; total posts: '+str(len(db))+'\n')
	d['all']=db

###############################################################################

@service
@err
def wifi(d):
	try:
		if loads(check_output('termux-wifi-connectioninfo'))['supplicant_state'] == 'COMPLETED':
			wifi_c=1
		else:
			wifi_c=0
	except:
		print('unable to check if internet is over wifi or mobile data, try to run vkfeed/install\n')
		wifi_c=1
	d['wifi']=wifi_c

###############################################################################

@err
def sysfree():
	cu=mu=0
	try:
		t=check_output(['ps','-eo','%cpu,%mem']).decode().split('\n')
		t=t[1:-1]
		t=[w.split() for w in t]
		t=list(zip(*t))
		cu=sum(map(float,t[0]))/100
		mu=sum(map(float,t[1]))/100
		t=check_output(['top','-b','-n','1']).decode().split('\n')
		t=[w.split('%') for w in t]
		t=[w[0] for w in t if len(w)>1 and w[0].isdigit() and w[1].startswith('cpu')][0]
		cu*=100
		cu/=float(t)
	except:
		pass
	try:
		t=check_output(['top','-b','-n','1']).decode().split('\n')
		t=[w if w.strip() else '' for w in t]
		t=t[1:t.index('')]
		t=[w.split(':',1) for w in t]
		for w in t:
			w[1]=w[1].replace(',','.').split('. ')
			w[1]=[e.strip().split(' ',1)[::-1] for e in w[1]]
			w[1]=dict(w[1])
		t=dict(t)
		cpu=t[[w for w in t if 'cpu' in w.lower()][0]]
		cpu_f=float(cpu['id'])/100
		mem=t[[w for w in t if 'mem' in w.lower()][0]]
		mu=float(mem['used'])/float(mem['total'])
		cu=1-cpu_f
	except:
		pass
	if cu<0.3 and mu<0.9:
		return 1
	return 0

###############################################################################

@err
def manager():
	vk_token=token()
	start_=None
	while 1:
		try:
			sleep(0.3344554433)
			q=api('newsfeed.get?filters=post&max_photos=100&count=100'+('&start_from='+start_ if start_ else ''))
			try:
				start_=q['next_from']
			except:
				start_=None
			feed(q)
		except:
			error()

@err
def feed(q):
	for w in q['items']:
		if 'text' not in w:
			w['text']=''
		w['source_name']=''
		try:
			if w['source_id']<0:
				d=[e for e in q['groups'] if e['id']+w['source_id']==0]
				d=d[0]
				d=d['name']
				w['source_name']=d
			else:
				d=[e for e in q['profiles'] if e['id']==w['source_id']]
				d=d[0]
				d=d['first_name']+' '+d['last_name']
				w['source_name']=d
		except:
			error()
		w['original']=str(w['source_id'])+'_'+str(w['post_id'])
	q=q['items']
	for w in q:
		if 'marked_as_ads' not in w:
			w['marked_as_ads']=0
	q=[w for w in q if w['marked_as_ads']==0]
	for w in q:
		process(postworker,(w,),force=0)

def postworker(w):
	photodata=bytearray()
	w['photos']=[]
	if 'attachments' not in w:
		w['attachments']=[]
	date=str(w['date'])
	orig=w['original']
	for e in w['attachments']:
		if e['type']=='photo':
			e=e['photo']
			e['sizes']=[r for r in e['sizes'] if r['type'] not in 'opqr']
			a=0
			for r in e['sizes']:
				if r['width']<729:
					a=max(a,r['width'])
			if a==0:
				a=e['sizes'][0]['width']
			size=[r for r in e['sizes'] if r['width']==a][0]
			url=size['url']
			size=[size['width'],size['height']]
			w['photos'].append(len(photodata))
			photodata+=urlopen(url).read()
	w={'date':str(w['date']),'public':w['source_name'],'orig':w['original'],'text':w['text'],'photos':w['photos']}
	postname=w['date']+w['orig']
	w=dumps(w)
	w+='\0'
	w=w.encode()
	w=bytearray(w)
	w+=photodata
	open('post/'+postname,'wb').write(w)


###############################################################################

@service
@err
def cacheclear(d):
	if disk_usage(cache).used>disk_usage(cache).total*0.95:
		a=sorted(listdir('img/')+listdir('post/'))
		for w in a:
			try:
				remove('post/'+w)
			except:
				pass
			if disk_usage(cache).used<disk_usage(cache).total*0.9:
				break

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
			db=get_db()
			if len(db)>1:
				db=[w for w in db if w!='00_0']
			db=[{'url':w} for w in db]
			self.send_response(200)
			self.send_header("Content-type", "text/json; charset=utf-8")
			self.end_headers()
			db=dumps(db)
			self.wfile.write(db.encode())
			return
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

token()

hostPort = 9836

st=1
while st:
	try:
		myServer = HTTPServer(('127.0.0.1', hostPort), MyServer)
		st=0
	except:
		hostPort+=1

print("http://127.0.0.1:%s" % (hostPort))
try:
	run(["termux-open-url","http://127.0.0.1:%s" % (hostPort)])
except:
	pass

process(service_run)
process(manager)

def stopserver(server):
	sleep(0.2)
	server.server_close()
	print('stopped')

def runserver():
	try:
		myServer.serve_forever()
	except KeyboardInterrupt:
		pass
	myServer.server_close()
	
try:
	myServer.serve_forever()
except KeyboardInterrupt:
	killer()
killer()

myServer.server_close()
print()