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
try:
	from shutil import disk_usage
except:
	try:
		from psutil import disk_usage
	except:
		from shutil import disk_usage
from pprint import pprint
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote as uqu
from os import getpid
from os.path import exists
from os import remove
from functools import partial

###############################################################################

home=str(Path.home())+'/'
cache=home+'.vkfeed/'
if not exists(cache):
	mkdir(cache)
chdir(cache)
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
	def run(*q,**w):
		try:
			return func(*q,**w)
		except KeyboardInterrupt:
			killer()
		except:
			error()
	run.f_n=func.__name__
	return run

def killer():
	p=str(getpid())
	pid=open('pid').read().split('\n')
	end=open('end').read().split('\n')
	for w in pid:
		if w != p and w not in end:
			kill(int(w),SIGTERM)
	exit()

###############################################################################

@err
def process(p,a=()):
	def run(*q,**w):
		open('pid','a').write(str(getpid())+'\n')
		try:
			p(*q,**w)
		except KeyboardInterrupt:
			killer()
		except:
			error()
		open('end','a').write(str(getpid())+'\n')
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
		sleep(4)

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
		db=loads('['+open('db.json').read().strip().replace('\n',',')+']')
	except:
		db=[]
	return db

@err
def addits_db(a):
	a=a[:]
	a=[dumps(w)+'\n' for w in a]
	a=''.join(a)
	if exists('db.json'):
		open('db.json','a').write(a)
	else:
		print('j')
		open('db.json','w').write(a)

###############################################################################

@err
def token():
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
		print(ret)

###############################################################################

@service
@err
def monitor(d):
	l=len(get_db())
	try:
		if l==d['l']==0:
			remove('db.json')
	except:
		pass
	print(asctime(),l,'posts in cache')
	d['l']=l

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
		print('unable to check if internet is over wifi or mobile data, try to run vkfeed/install')
		wifi_c=1
	d['wifi']=wifi_c

###############################################################################

@service
@err
def sysmon(d):
	t=check_output(['ps','-eo','%cpu,%mem']).decode().split('\n')
	t=t[1:-1]
	t=[w.split() for w in t]
	t=list(zip(*t))
	cu=sum(map(float,t[0]))
	mu=sum(map(float,t[1]))
	'''
	t=check_output(['top','-b','-n','1']).decode().split('\n')
	t=[w if w.strip() else '' for w in t]
	t=t[1:t.index('')]
	t=[w.split(':',1) for w in t]
	for w in t:
		w[1]=w[1].split(',')
		w[1]=[e.strip().split(' ',1)[::-1] for e in w[1]]
		w[1]=dict(w[1])
	t=dict(t)
	cpu=t[[w for w in t if 'cpu' in w.lower()][0]]
	cpu_f=float(cpu['id'])/100
	mem=t[[w for w in t if 'mem' in w.lower()][0]]
	mem_f=float(mem['free'])/float(mem['total'])
	'''
	print(cu,mu)
	if cu<64 and mu<64:
		d['sysmon']=1
	else:
		d['sysmon']=0

###############################################################################

@err
def manager():
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
	service_wait('sysmon')
	for w in q:
		process(postworker,(w,))	

@err
def postworker(w):
	w['photos']=[]
	if 'attachments' not in w:
		w['attachments']=[]
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
			name=str(time())+'.'+url.split('/')[-1].split('?')[0]
			open(name,'wb').write(urlopen(url).read())
			sm=check_output(['sum',name]).decode()
			w['photos'].append({'name':name,'sum':sm,'size':size})
	w={'date':str(w['date']),'public':w['source_name'],'orig':w['original'],'text':w['text'],'photos':w['photos']}
	db=get_db()
	if [e for e in db if postsame(e,w)]==[]:
		if w['text'] or w['photos']:
			addits_db([w])


@err
def postsame(a,s):
	return textsame(a['text'],s['text']) and set([r['sum'] for r in a['photos']])==set([r['sum'] for r in s['photos']])

@service
@err
def cacheclear(d):
	while disk_usage(cache).free<2*1024**3:
		remove(sorted([w for w in listdir(cache) if w[0] in '1234567890'])[0])

@err
def textsame(q,w):
	q=list(ndiff(q,w))
	return len([w for w in q if w.startswith('  ')])*2>len(q)

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
		elif path=='json':
			db=get_db()
			self.send_response(200)
			self.send_header("Content-type", "text/json; charset=utf-8")
			self.end_headers()
			keys=db[:]
			keys.sort(key=lambda f:f['date'])
			for w in keys:
				w['photos']=[e['name'] for e in w['photos']]
			keys=keys[::-1]
			if len(keys)==0:
				keys.append({'date':'0.0.0','public':'vkfeed','text':'creating cache...\n wait 10 mintes and refresh','orig':'0_0','photos':[]})
			keys=dumps(keys)
			self.wfile.write(keys.encode())
		elif '/' not in path:
			if path[0] in '1234567890' and '/' not in path:
				path=path
			elif path[0] in 'qwertyuiopasdfghjklzxcvbnm' and '/' not in path:
				path=repo+path
			try:
				self.send_response(200)
				self.send_header("Content-type", "file/file")
				self.end_headers()
				self.wfile.write(open(path,'rb').read())
			except:
				self.send_response(404)
				self.send_header("Content-type", "file/file")
				self.end_headers()

###############################################################################

process(service_run)

token()

try:
	remove('lock')
except:
	pass

hostPort = 9876

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

process(manager)

try:
	myServer.serve_forever()
except KeyboardInterrupt:
	killer()
killer()

myServer.server_close()
print()
