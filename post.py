''':'
python3 $0 $@
exit
':'''

###############################################################################

from urllib.request import urlopen as urlop
from json import loads
from json import dumps
from urllib.parse import quote as qu
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
from functools import reduce
from functools import wraps
from base64 import b64encode
from base64 import b64decode
from io import BytesIO

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

def ppr(*q,**w):
	print(*q,**w)

def pppr(*q,**w):
	pprint(*q,**w)

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
		ppr(q)
	except:
		pppr(q,format_exc())

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
		ppr(asctime()+' new downloaded: '+str(news)+'\t   old deleted: '+str(dels)+'\t   total posts: '+str(len(db))+'')
	else:
		ppr(asctime()+'; total posts: '+str(len(db))+'')
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
		ppr('unable to check if internet is over wifi or mobile data, try to run vkfeed/install')
		wifi_c=1
	shared['wifi']=wifi_c

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
	ppr('https://oauth.vk.com/authorize?client_id=7623880&scope=73730&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token&revoke=1')
	url=input('now paste the url: ')
	t=url.split('#')[1].split('&')[0].split('=')[1]
	open('token','w').write(t)
	return t

vk_token=token()

###############################################################################

@err
def curl(q,data=None):
	try:
		db=loads(open('curl.json').read())
	except:
		db={}
	key=b64encode(q.encode()).decode()+'_'+b64encode(b'_' if data==None else data).decode()
	if key in db:
		return BytesIO(b64decode(db[key].encode()))
	sleep(1/4)
	w=urlop(q,data=data).read()
	db[key]=b64encode(w).decode()
	open('curl.json','w').write(dumps(db))
	return BytesIO(w)

@err
def urlopen(*q,**w):
	while 1:
		try:
#			u=urlop(*q,**w)
			u=curl(*q,**w)
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
#	sleep(1/4)
	ret=loads(urlopen('https://api.vk.com/method/'+path+'v=5.101&access_token='+token(),data=data).read().decode())
	try:
		if 'error' in ret:
			ppr(ret['error']['error_msg'])
	except:
		pppr(ret)
	try:
		return items(ret['response'])
	except:
		pass

###############################################################################

@err
def feedget(sf=None):
	osf=sf
	sk=0
	res=api('execute.feedget'+('?start_from='+sf if sf else ''))
	sf,res=res
#	print(len(res['items']['date']))
	resitems=res['items']
	oritems=[]
	for e in range(len(resitems.values().__iter__().__next__())):
		d=dict()
		for r in resitems.keys():
			d[r]=resitems[r][e]
		if not d['marked_as_ads'] and not exists('post/'+str(d['date'])+str(d['source_id'])+'_'+str(d['post_id'])):
			oritems.append(d)
		else:
			sk+=1
	a={}
	a['items']=[]
	a['groups']=[]
	a['profiles']=[]
	if sk<len(oritems):
		return [0,osf,a]
	items=[str(d['source_id'])+'_'+str(d['post_id']) for d in oritems]
	groups=[str(-d['source_id']) for d in oritems if d['source_id']<0]
	profiles=[str(d['source_id']) for d in oritems if d['source_id']>0]
	items.sort()
	groups.sort()
	profiles.sort()
	items=reduce(lambda l,x: l if l and l[-1]==x else l+[x],items,[])
	groups=reduce(lambda l,x: l if l and l[-1]==x else l+[x],groups,[])
	profiles=reduce(lambda l,x: l if l and l[-1]==x else l+[x],profiles,[])
	while groups:
		a['groups']+=api('groups.getById','group_ids='+','.join(groups[:500]))
		groups=groups[500:]
	while profiles:
		a['profiles']+=api('users.get','user_ids='+','.join(profiles[:1000]))
		profiles=profiles[1000:]
	while items:
		gg=items[:100]
#		a['items']+=api('wall.getById','posts='+gg)
		d=api('wall.getById','posts='+','.join(gg))
		hh=[str(w['owner_id'])+'_'+str(w['id']) for w in d]
		jj=ndiff(hh,gg)
		jj=[w for w in jj if w[0]=='-']
		if jj:
			print(jj)
			raise KeyboardInterrupt
		a['items']+=d
		items=items[100:]
	for w in a['items']:
		w['source_id']=w['owner_id']
		w['post_id']=w['id']
	return [sk,sf,a]

###############################################################################

@err
def pageget(sf=None):
	q=api('newsfeed.get?filters=post&max_photos=100&count=100'+('&start_from='+sf if sf else ''))
	try:
		sf=q['next_from']
	except:
		sf=None
	sk=len(q['items'])
	q['items']=[d for d in q['items'] if not (d['marked_as_ads'] if 'marked_as_ads' in d else 0) and not exists('post/'+str(d['date'])+str(d['source_id'])+'_'+str(d['post_id']))]
	sk-=len(q['items'])
	return [sk,sf,q]

###############################################################################

@setinterval(0.13344554433)
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
	if 'sk' not in shared.keys():
		shared['sk']=0
#	pageget=feedget##########
	sk,sf,q=feedget(sf) if shared['sk'] else pageget(sf)
	shared['start']=sf
	shared['sk']=0
	if sk>60:
		shared['sk']=1
	names=dict([[-w['id'],w['name']] for w in q['groups']]+[[w['id'],w['first_name']+' '+w['last_name']] for w in q['profiles']])
	q=q['items']
	print('to work',len(q),'other',sk)
	for w in q:
		print(q.index(w))
		if 'text' not in w:
			w['text']=''
		postname=str(w['date'])+str(w['source_id'])+'_'+str(w['post_id'])
		if exists('post/'+postname):
			print('exists2')
		photodata=bytearray()
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
				w['photos'].append(len(photodata))
				photodata+=urlopen(url).read()
		w={'date':str(w['date']),'public':names[w['source_id']],'orig':str(w['source_id'])+'_'+str(w['post_id']),'text':w['text'],'photos':w['photos']}
		w=dumps(w)
		w+='\0'
		w=w.encode()
		w=bytearray(w)
		w+=photodata
		open('post/'+postname,'wb').write(w)

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
