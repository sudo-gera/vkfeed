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
class object: pass

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
			raise KeyboardInterrupt()
		except:
			error()
	return run

###############################################################################

fs=[]

@err
def setinterval(t):
	def wrapper(t,f):
		fs.append([f,t,time()])
	return partial(wrapper,t)

###############################################################################
###############################################################################

@setinterval(60)
@err
def cacheclear():
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

@setinterval(30)
@err
def monitor():
	try:
		db=sorted(listdir('post/'))[::-1]
	except:
		db=[]
	if 'all' in shared:
		news=0
		dels=0
		dc=0
		sc=0
		sb=shared['all']
		while dc<len(db) and sc<len(sb):
			if db[dc]==sb[sc]:
				dc+=1
				sc+=1
			elif db[dc]<sb[sc]:
				dels+=1
				sc+=1
			elif db[dc]>sb[sc]:
				news+=1
				dc+=1
		print(asctime()+' new downloaded: '+str(news)+'\t   old deleted: '+str(dels)+'\t   total posts: '+str(len(db))+'\n')
	else:
		print(asctime()+'; total posts: '+str(len(db))+'\n')
	shared['all']=db

###############################################################################

@setinterval(10)
@err
def wifi():
	try:
		if loads(check_output('termux-wifi-connectioninfo'))['supplicant_state'] == 'COMPLETED':
			wifi_c=1
		else:
			wifi_c=0
	except:
		print('unable to check if internet is over wifi or mobile data, try to run vkfeed/install\n')
		wifi_c=1
	shared['wifi']=wifi_c

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
	if cu<0.5 and mu<0.9:
		return 1
	return 0

###############################################################################
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

vk_token=token()

###############################################################################

@err
def urlopen(*q,**w):
	while 1:
		try:
			u=urlop(*q,**w)
			shared['internet']=1
			break
		except:
			shared['internet']=0
			sleep(4)
	return u

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

###############################################################################

@err
def api(path,data=''):
	if path and path[-1] not in '&?':
		if '?' in path:
			path+='&'
		else:
			path+='?'
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

@err
def feedget(sf=None):
	res=api('execute.feedget'+('&start_from='+sf if sf else ''))
	print('filesize',len(res))
	sf,res=res
	uids=res['profiles']['id'][:]
	c=0
	while uids:
		q=api('users.get?ids='+','.join(uids[:1000]))
		uids=uids[1000:]
		for t in q:
			res['profiles']['first_name'][c]=t['first_name']
			res['profiles']['last_name'][c]=t['last_name']
			res['profiles']['id'][c]=t['id']
			c+=1
	a={}
	for w in res.keys():
		a[w]=[]
		for e in range(len(res[w].vaues().__iter__().__next__())):			
			d=dict()
			for r in res[w].keys():
				d[e]=res[w][r][e]
			a[w].append(d)
	return [sf,a]

###############################################################################

@err
def pageget(sf=None):
	q=api('newsfeed.get?filters=post&max_photos=100&count=100'+('&start_from='+sf if sf else ''))
	try:
		sf=q['next_from']
	except:
		sf=None
	return [sf,q]

###############################################################################

@setinterval(0.3344554433)
@err
def feed():
	if 'internet' in shared and not shared['internet']:
		return
	try:
		sf=shared['start']
	except:
		sf=None
	if 'wifi' in shared and not shared['wifi']:
		return
	sf,q=pageget(sf)
	for w in q['items']:
		if 'text' not in w:
			w['text']=''
		w['source_name']=''
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
		w['original']=str(w['source_id'])+'_'+str(w['post_id'])
	q=q['items']
	for w in q:
		if 'marked_as_ads' not in w:
			w['marked_as_ads']=0
	q=[w for w in q if w['marked_as_ads']==0]
	for w in q:
		postname=str(w['date'])+w['original']
		if exists('post/'+postname):
			pass
		else:
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
	shared['start']=sf

###############################################################################
###############################################################################

shared=dict()
while 1:
	t=time()
	for w in fs:
		if w[2]<t:
			w[0]()
			w[2]=t+w[1]
	m=float('inf')
	for w in fs:
		m=min(m,w[2])
	sleep(max(m-t,0))
	if exists('exit'):
		exit()
