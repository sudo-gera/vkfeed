''':'
python3 $0 $@
exit
':'''


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
try:
	from shutil import disk_usage
except:
	from psutil import disk_usage

home=str(Path.home())+'/'
cache=home+'.vkfeed/'

def error():
	q=format_exc()
	try:
		q=q.split('\n')
		f=q[1:-2]
		d=[]
		while f:
			d.append(f[:2])
			f=f[2:]
		d=d+[w for w in d if w[0].split('"')[1].split('/')[-1]=='vkfeed']
		d=d[-1]
		d='line'+d[0].split('line',1)[1]
		q=d+', '+q[-2]
		print(q)
	except:
		print(q,format_exc())

try:
	repo=open(cache+'path').read()
except:
	repo = str(abspath(dirname(argv[0])))
	if repo[-1]!='/':
		repo+='/'
	open(cache+'path','w').write(repo)

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


neew_new=1
wifi_de=64
wifi_er=0
wifi_en=wifi_de

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

def wifi():
	global wifi_en,wifi_er,wifi_de
	if wifi_er:
		return 1
	try:
		if wifi_en<wifi_de:
			wifi_en+=1
			return 1
		else:
			if loads(check_output('termux-wifi-connectioninfo'))['supplicant_state'] == 'COMPLETED':
				wifi_en=0
				return 1
			else:
				return 0
	except:
		if wifi_er==0:
			print('unable to check if internet is over wifi or mobile data, try to run\npkg install termux-api')
			wifi_er=10
		else:
			wifi_er-=1
		return 1

def manager():
	d=None
	global neew_new
	try:
		if neew_new:
			pass
	except:
		neew_new=1
	while 1:
		if neew_new:
			try:
				d=feed()
				neew_new=0
			except:
				error()
		else:
			try:
				d=feed(d)
			except:
				error()
	
def feed(start_=None):
	global db
	sleep(0.3333334)
	q=api('newsfeed.get?filters=post&max_photos=100&count=100'+('&start_from='+start_ if start_ else ''))
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
	try:
		next_=q['next_from']
	except:
		next_=None
	q=q['items']
	for w in q:
		w['photos']=[]
		if 'attachments' not in w:
			w['attachments']=[]
		for e in w['attachments']:
			if e['type']=='photo':
				e=e['photo']
				e['sizes']=[r for r in e['sizes'] if r['type'] not in 'opqr']
				a=0
				for r in e['sizes']:
					a=max(a,r['width'])
				url=[r for r in e['sizes'] if r['width']==a][0]['url']
				name=str(time())+'.'+url.split('/')[-1].split('?')[0]
				while wifi()==0:
					sleep(4)
				sleep(0.3344554433)
				cacheclear()
				open(cache+name,'wb').write(urlopen(url).read())
				sm=check_output(['sum',cache+name]).decode()
				w['photos'].append({'name':name,'sum':sm})
	q=[[str(w['date'])+'.'+str(time()),{'public':w['source_name'],'orig':w['original'],'text':w['text'],'photos':w['photos']}] for w in q]
	q=dict(q)
	for w in q:
		if [e for e in db.keys() if db[e]['orig']==q[w]['orig']]==[]:
			if [e for e in db.keys() if db[e]['text']==q[w]['text'] and sorted([r['sum'] for r in db[e]['photos']]) == sorted([r['sum'] for r in db[e]['photos']])]==[]:
				db[w]=q[w]
		else:
			next_=None
	open(cache+'db.json','w').write(dumps(db))
	print(asctime(),'some new posts are loaded')
	return next_

if not exists(cache):
	mkdir(cache)

try:
	db=loads(open(cache+'db.json').read())
except:
	db=dict()

cachecleared=0
def cacheclear():
	global cache,cachecleared
	if cachecleared:
		cachecleared-=1
		return
	cachecleared=10
	while disk_usage(cache).free<2*1024**3:
		remove(sorted([w for w in listdir(cache) if w[0] in '1234567890'])[0])

proc=Process(target=manager)
token()
proc.start()

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote as uqu
import os


class MyServer(BaseHTTPRequestHandler):
	def do_GET(self):
		global cache,repo
		self.send_response(200)
		path=self.path
		path,arg=(path.split('?',1)+[''])[:2]
		path=uqu(path)
		if path[0]=='/':
			path=path[1:]
		if path=='':
			try:
				db=loads(open(cache+'db.json').read())
			except:
				db=dict()
			self.send_header("Content-type", "text/html; charset=utf-8")
			self.end_headers()
			self.wfile.write(open(repo+'feed.html','r').read().encode())
		elif path=='json':
			try:
				db=loads(open(cache+'db.json').read())
			except:
				try:
					_db=db
				except:
					db=dict()
			self.send_header("Content-type", "text/html; charset=utf-8")
			self.end_headers()
#			keys=list(db.keys())
#			keys=sorted(keys)[::-1]
#			keys=['<!--'+w+'--><div class=post id='+w+'><h3>'+db[w]['public']+'</h3><h6>'+'<a target="_blank" href=https://vk.com/wall'+db[w]['orig']+'>original</a></h6><h5>'+db[w]['text']+'</h5><br>'+''.join(['<img src='+e+' width="100%"><br>' for e in db[w]['photos']])+'</div>' for w in keys]
#			keys='\n'.join(keys)
			keys=[{'date':w,**db[w]} for w in sorted(list(db.keys()))]
			keys=[w for w in keys if w['text'] or w['photos']]
			for w in keys:
				w['photos']=[e['name'] for e in w['photos']]
			keys=keys[::-1]
			if len(keys)==0:
				keys.append({'date':'0.0.0','public':'vkfeed','text':'creating cache...\n wait 10 mintes and refresh','orig':'0_0','photos':[]})
			keys=dumps(keys)
			loads(keys)
			self.wfile.write(keys.encode())
		elif path[0] in '1234567890' and '/' not in path:
			self.send_header("Content-type", "file/file")
			self.end_headers()
			self.wfile.write(open(cache+path,'rb').read())
		elif path[0] in 'qwertyuiopasdfghjklzxcvbnm' and '/' not in path:
			self.send_header("Content-type", "file/file")
			self.end_headers()
			self.wfile.write(open(repo+path,'rb').read())
	def log_message(*a):
		pass


hostPort = 9876

st=1
while st:
 try:
  myServer = HTTPServer(('127.0.0.1', hostPort), MyServer)
  st=0
 except:
  hostPort+=1

try:
	run(["termux-open-url","http://127.0.0.1:%s" % (hostPort)])
except:
	print("http://127.0.0.1:%s" % (hostPort))

try:
    myServer.serve_forever()
except KeyboardInterrupt:
    pass

proc.terminate()
myServer.server_close()
print()
