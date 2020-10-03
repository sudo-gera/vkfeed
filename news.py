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
from subprocess import run
from webbrowser import open as webopen
from sys import argv
from pathlib import Path
from pprint import pprint
from multiprocessing import Process

home=str(Path.home())+'/'

url=open(str(Path.home())+'/url').read()
token=url.split('#')[1].split('&')[0].split('=')[1]

neew_new=1
wifi_en=10

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
	global token
	ret= loads(urlopen('https://api.vk.com/method/'+path+'v=5.101&access_token='+token,data=data).read().decode())
	try:
		return items(ret['response'])
	except:
		pass
	try:
		print(ret['error']['error_msg'])
	except:
		print(ret)

def wifi():
	global wifi_en
	try:
		if wifi_en<10:
			wifi_en+=1
			return 1
		else:
			if loads(popen('termux-wifi-connectioninfo').read())['supplicant_state'] == 'COMPLETED':
				wifi_en=0
				return 1
			else:
				return 0
	except:
		print(error())
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
			d=feed()
			neew_new=0
		else:
			d=feed(d)
	
def feed(start_=None):
	global db
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
				d=[e for e in q['groups'] if e['id']+w['source_id']==0]
				d=d[0]
				d=d['first_name']+' '+d['last_name']
				w['source_name']=d
		except:
			print(error())
		w['original']=str(w['source_id'])+'_'+str(w['post_id'])
	next_=q['next_from']
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
				sleep(0.1)
				open(home+'.vkfeed/'+name,'wb').write(urlopen(url).read())
				w['photos'].append(name)
	q=[[str(w['date'])+'.'+str(time()),{'public':w['source_name'],'orig':w['original'],'text':w['text'],'photos':w['photos']}] for w in q]
	q=dict(q)
	for w in q:
		db[w]=q[w]
	open(home+'.vkfeed/db.json','w').write(dumps(db))
	return next_

if not exists(home+'.vkfeed'):
	mkdir(home+'.vkfeed')

try:
	db=loads(open(home+'.vkfeed/db.json').read())
except:
	db=dict()

Process(target=manager).start()

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote as uqu
import os


def makepage(keys):
	return ['<!--'+w+'--><div class=post><h3>'+db[w]['public']+'</h3><h6><a href=https://vk.com/wall'+db[w]['orig']+'>original</a></h6><h5>'+db[w]['text']+'</h5>'+''.join(['<h6><img src='+e+'>' for e in db[w]['photos']])+'</div>\n' for w in keys]

class MyServer(BaseHTTPRequestHandler):
	def do_GET(self):
		self.send_response(200)
		path=self.path
		path,arg=(path.split('?',1)+[''])[:2]
		path=uqu(path)
		path=path[1:]
		if path=='':
			self.send_header("Content-type", "text/html; charset=utf-8")
			self.end_headers()
			self.wfile.write(open(argv[0]+'.html','rb').read())
		elif path == 'favicon.ico':
			self.send_header("Content-type", "file/file")
			self.end_headers()
			self.wfile.write(open(argv[0]+'.favicon.ico','rb').read())
		elif path == 'load':
			self.send_header("Content-type", "text/html; charset=utf-8")
			self.end_headers()
			keys=list(db.keys())
			keys=sorted(keys)[-8:][::-1]
			keys=makepage(keys)
			keys=dumps(keys)
			self.wfile.write(keys.encode())
		elif path.startswith('page_<!--'):
			path=path[9:]
			self.send_header("Content-type", "text/html; charset=utf-8")
			self.end_headers()
			keys=list(db.keys())
			keys=sorted(keys)
			keys=[w for w in keys if w<path][-8:][::-1]
			keys=makepage(keys)
			keys=dumps(keys)
			self.wfile.write(keys.encode())
		else:
			self.send_header("Content-type", "file/file")
			self.end_headers()
			self.wfile.write(open(home+'.vkfeed/'+path,'rb').read())


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
	import webbrowser
	print("http://127.0.0.1:%s" % (hostPort))

try:
    myServer.serve_forever()
except KeyboardInterrupt:
    pass

myServer.server_close()
print()
