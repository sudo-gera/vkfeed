from browser import *
from browser import ajax
from browser import timer
from browser import local_storage
from browser import window
from browser import document
from time import time
from json import loads

urlopen_dict=dict()
def urlopen_read(t,f):
    urlopen_dict[t]=f.read()
def urlopen(url):
	t=time()
	req = ajax.get(url,True,oncomplete=lambda a:urlopen_read(t,a))
	return loads(urlopen_dict[t])



def setCookie(name,value):
	local_storage.storage[name]=value


def getCookie(name):
	if name not in local_storage.storage:
		return None
	return local_storage.storage[name]



posts=[]
body=0
start=0
postsinpage=8
del_=0

def log(q):
	document.getElementById('log').value+=''+q+'\n'


def getpost(i):
	return document.getElementById('_'+str(i))


def autodel():
	statst=start
	op=getpost(statst).getBoundingClientRect().bottom
	for i in range(del_,statst):
		delpost(i)
	
	del_=statst
	window.scrollBy(0,op-getpost(statst).getBoundingClientRect().bottom)



def delpost(i):
	getpost(i).parentNode.removeChild(getpost(i))


def onscroll():
	newposts=getoverpage()
	if (newposts!=None):
		global start
		newposts-=start
		i=start+postsinpage
		while i<start+newposts+postsinpage and i<len(posts):
			if (posts[i]['posted']==0):
				body.innerHTML+=posttotext(posts[i])
				posts[i]['posted']=1
			i+=1
		
		bot1=getpost(start+newposts).getBoundingClientRect().bottom
		i=start
		while i<start+newposts and i<len(posts):
			delpost(i)
			i+=1
		
		bot2=getpost(start+newposts).getBoundingClientRect().bottom
		window.scrollBy(0,-bot1+bot2)
		start+=newposts
		if (start>len(posts)):
			start=len(posts)
		
		setCookie('start',posts[start]['url'])
	
timer.set_interval(onscroll,3000)


def getoverpage(st=None,fi=None):
	if (st==None):
		st=start
	
	if (fi==None):
		fi=start+postsinpage
	
	if (fi>len(posts)):
		fi=len(posts)
	
	if (len(posts)==0):
		console.log('len=0')
		return
	
	try:
		if (getpost(st).getBoundingClientRect().bottom>=0):
			return
	except:
		return

	if (fi<=st):
		console.log('len<0')
		return
	
	if (fi-st==1):
		return st
	
	ce=round((fi+st)/2)
	if (getpost(ce).getBoundingClientRect().bottom<0):
		return getoverpage(ce,fi)
	
	return getoverpage(st,ce)


def posttotext(q):
	oq=q
	json=urlopen('/post/'+q['url'])
	
	q=json
	text='<br><h1>'+q['public']+'</h1><h3>'+q['text']+'</h3><br>'
	for photo in q['photos']:
		text+='\n<img src="data:image/png;base64,'+photo+' "width="100%"><br>'
	
	text+='\n<div class="orig"><h3><a target="_blank" href=https://vk.com/wall'+q['orig']+'><img height="64px" src=orig.png width="64px"></a></h3></div>'
	text='<div class=post id=_'+str(oq['index'])+'>'+text+'</div>\n'
	return text


def up(*q):
	setCookie('up','1')
	document.location.reload()

document.getElementById('upbutton').bind('click',up)

def onload():
	global body
	body=document.getElementById('body')
	json=urlopen('/json')
	global posts
	posts=json[:]
	start=0
	cs=getCookie('start')
	i=0
	if (getCookie('up')=='1'):
		setCookie('up','0')
		cs=None
	
	for post in posts:
		post['index']=i
		post['posted']=0
		if (cs==post['url']):
			start=i
		
		i+=1

	body.innerHTML=''
	i=start;
	while i<len(posts) and i<postsinpage+start:
		body.innerHTML+=posttotext(posts[i])
		posts[i].posted=1
		i+=1

	del_=start
onload()