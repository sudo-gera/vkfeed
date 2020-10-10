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
from traceback import format_exc as error
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

home=str(Path.home())+'/'
path=open(home+'.vkfeed/path').read()

def token(check=0):
	try:
		return open(home+'.vkfeed/token').read()
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
	open(home+'.vkfeed/token','w').write(t)


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
#			wifi_er=1
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
				print(error())
		else:
			try:
				d=feed(d)
			except:
				print(error())
	
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
			print(error())
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
				open(home+'.vkfeed/'+name,'wb').write(urlopen(url).read())
				w['photos'].append(name)
	q=[[str(w['date'])+'.'+str(time()),{'public':w['source_name'],'orig':w['original'],'text':w['text'],'photos':w['photos']}] for w in q]
	q=dict(q)
	for w in q:
		if [e for e in db.keys() if db[e]['orig']==q[w]['orig']]==[]:
			db[w]=q[w]
		else:
			next_=None
	open(home+'.vkfeed/db.json','w').write(dumps(db))
	print(asctime(),'some new posts are loaded')
#	rename(home+'.vkfeed/db.json1',home+'.vkfeed/db.json')
	return next_

if not exists(home+'.vkfeed'):
	mkdir(home+'.vkfeed')

try:
	db=loads(open(home+'.vkfeed/db.json').read())
except:
	db=dict()

tn=time()
for w in listdir(home+'/vkfeed/'):
	w=w.split('.')
	try:
		if int(w[1])<tn-3600*24*7:
			remove(home+'/vkfeed/'+'.'.join(w))
	except:
		pass

proc=Process(target=manager)
token()
proc.start()

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote as uqu
import os


def makepage(keys):
	return ['<!--'+w+'--><div class=post><h3>'+db[w]['public']+'</h3><h6>'+'<a target="_blank" href=https://vk.com/wall'+db[w]['orig']+'>original</a></h6><h5>'+db[w]['text']+'</h5><br>'+''.join(['<img src='+e+' width="1000vw"><br>' for e in db[w]['photos']])+'</div>\n' for w in keys]

class MyServer(BaseHTTPRequestHandler):
	def do_GET(self):
		self.send_response(200)
		path=self.path
		path,arg=(path.split('?',1)+[''])[:2]
		path=uqu(path)
		if path[0]=='/':
			path=path[1:]
		if path=='':
			try:
				db=loads(open(home+'.vkfeed/db.json').read())
			except:
				db=dict()
			self.send_header("Content-type", "text/html; charset=utf-8")
			self.end_headers()
			self.wfile.write(open(path+'feed.html','r').read().encode())
		elif path=='json':
			try:
				db=loads(open(home+'.vkfeed/db.json').read())
			except:
				pass
			self.send_header("Content-type", "text/html; charset=utf-8")
			self.end_headers()
#			keys=list(db.keys())
#			keys=sorted(keys)[::-1]
#			keys=['<!--'+w+'--><div class=post id='+w+'><h3>'+db[w]['public']+'</h3><h6>'+'<a target="_blank" href=https://vk.com/wall'+db[w]['orig']+'>original</a></h6><h5>'+db[w]['text']+'</h5><br>'+''.join(['<img src='+e+' width="100%"><br>' for e in db[w]['photos']])+'</div>' for w in keys]
#			keys='\n'.join(keys)
			keys=[{'date':w,**db[w]} for w in sorted(list(db.keys()))]
			keys=[w for w in keys if w['text'] or w['photos']]
			keys=keys[::-1]
			if len(keys)==0:
				keys.append({'date':'0.0.0','public':'vkfeed','text':'creating cache...\n wait 10 mintes and refresh','orig':'0_0','photos':[]})
			keys=dumps(keys)
			loads(keys)
			self.wfile.write(keys.encode())
		elif path == 'favicon.ico':
			self.send_header("Content-type", "file/file")
			self.end_headers()
			self.wfile.write(open(path+'favicon.ico','rb').read())
		else:
			self.send_header("Content-type", "file/file")
			self.end_headers()
			try:
				self.wfile.write(open(home+'.vkfeed/'+path,'rb').read())
			except:
				self.wfile.write(open(path+'favicon.ico','rb').read())
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
