''':'
python3 $0 $@
exit
':'''

###############################################################################

from urllib.request import urlopen
from json import loads
from json import dumps
from urllib.parse import quote
from time import sleep
from time import time
from time import asctime
from traceback import format_exc
from os.path import exists
from os import mkdir
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
from difflib import ndiff
try:
	from shutil import disk_usage
except:
	from psutil import disk_usage
from pprint import pprint
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote as uqu
import os
from os.path import exists
from os import remove
from functools import partial

###############################################################################

def error():
	q=format_exc()
	try:
		q=q.split('\n')
		f=q[[e for e,w in enumerate(q) if w.startswith('Traceback')][-1]+1:-2]
		d=[]
		while f:
			d.append('\0'.join(f[:2]))
			f=f[2:]
		d=d+[w for w in d if argv[0] in w]
		d=d[-1]
		d='line'+d.split('line',1)[1]
		q=d+', '+q[-2]
		print(q)
	except:
		pprint(q,format_exc())

###############################################################################

home=str(Path.home())+'/'
cache=home+'.vkfeed/'
try:
	repo=open(cache+'path').read()
except:
	repo = str(abspath(dirname(argv[0])))
	if repo[-1]!='/':
		repo+='/'
	open(cache+'path','w').write(repo)

###############################################################################

os._a_a_=[]

def one_process(fun):
	def run(*q,**w):
		pid=os.getpid()
		os._a_a_.append(pid)
		while os._a_a_[0]!=pid:
			sleep(0.01)
		try:
			d=loads(open(cache+'vars.json').read())
		except:
			d=dict()
		r=fun(d,*q,**w)
		open(cache+'vars.json','w').write(dumps(d))
		os._a_a_=os._a_a_[1:]
		return r
	return run

###############################################################################

@one_process
def update_db(d,new_db=None):
	if new_db == None:
		try:
			db=loads(open(cache+'db.json').read())
		except:
			db=[]
	else:
		db=new_db
		open(cache+'db.json','w').write(dumps(db))
	return db

###############################################################################

def token(check=0):
	try:
		return open(cache+'token').read()
	except:
		if check:
			return
	input('welcome to vkfeed. you will be redirected to the authorization page, where you need to grant all the permissions required for the application to work. After that, you should copy the url of the page and paste it there.\nPress enter to open the page...')
	try:
		run(['termux-open-url','https://oauth.vk.com/authorize?client_id=7623880&scope=73730&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token&revoke=1'])
	except:
		print('https://oauth.vk.com/authorize?client_id=7623880&scope=73730&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token&revoke=1')
	url=input('now paste the url: ')
	t=url.split('#')[1].split('&')[0].split('=')[1]
	open(cache+'token','w').write(t)
	return t

###############################################################################

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

@one_process
def wifi(d):
	wifi_state=None
	if 'wifi_not_check' in d:
		wifi_not_check=d['wifi_not_check']
		if wifi_not_check:
			wifi_not_check-=1
			wifi_state=True
	if wifi_state==None:
		wifi_not_check=128
		try:
			if loads(check_output('termux-wifi-connectioninfo'))['supplicant_state'] == 'COMPLETED':
				wifi_state=True
			else:
				wifi_state=False
		except:
			print('unable to check if internet is over wifi or mobile data, try to run vkfeed/install')
			wifi_state=True
	d['wifi_not_check']=wifi_not_check
	return wifi_state

###############################################################################

def manager():
	start_=None
	while 1:
		try:
			sleep(0.3344554433)
			q=api('newsfeed.get?filters=post&max_photos=100&count=4'+('&start_from='+start_ if start_ else ''))
			try:
				start_=q['next_from']
			except:
				start_=None
			feed(q)
		except:
			error()

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
		procs.append(Process(target=postworker,args=(w,)).start())

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
			while wifi()==0:
				sleep(4)
			cacheclear()
			open(cache+name,'wb').write(urlopen(url).read())
			sm=check_output(['sum',cache+name]).decode()
			w['photos'].append({'name':name,'sum':sm,'size':size})
	w={'date':str(w['date'])+'.'+str(time()),'public':w['source_name'],'orig':w['original'],'text':w['text'],'photos':w['photos']}
	db=update_db()
	if [e for e in db if e['orig']==w['orig']]==[]:
		if [e for e in db if textsame(e['text'],w['text']) and set([r['sum'] for r in e['photos']]) == set([r['sum'] for r in w['photos']])]==[]:
			if w['text'] or w['photos']:
				db.append(w)
	else:
		next_=None
	update_db(db)

@one_process
def cacheclear(d):
	global cache
	if 'cache_recently_cleared' in d:
		cache_recently_cleared=d['cache_recently_cleared']
	else:
		cache_recently_cleared=0
	if cache_recently_cleared:
		cache_recently_cleared-=1
		return
	cache_recently_cleared=128
	while disk_usage(cache).free<2*1024**3:
		remove(sorted([w for w in listdir(cache) if w[0] in '1234567890'])[0])
	d['cache_recently_cleared']=cache_recently_cleared

def textsame(q,w):
	q=list(ndiff(q,w))
	return len([w for w in q if w.startswith('  ')])*2>len(q)
	
###############################################################################

class MyServer(BaseHTTPRequestHandler):
	def log_message(*a):
		pass
	def do_GET(self):
		global cache,repo
		path=self.path
		path=uqu(path)
		if path[0]=='/':
			path=path[1:]
		if path=='':
			path='feed.html'
			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.end_headers()
			self.wfile.write(open(path,'rb').read())
		if path=='json':
			db=update_db()
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
				path=cache+path
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

if not exists(cache):
	mkdir(cache)
procs=[]
proc=Process(target=manager)
token()
proc.start()

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

try:
    myServer.serve_forever()
except KeyboardInterrupt:
    pass

proc.terminate()
for w in procs:
	w.terminate()
myServer.server_close()
print()
