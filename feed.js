function getScrollPercent() {
var h = document.documentElement,
	b = document.body,
	st = 'scrollTop',
	sh = 'scrollHeight';
	return (h[st]||b[st]) / ((h[sh]||b[sh]) - h.clientHeight);
}

function setCookie(name,value){
	localStorage.setItem(name,value)
}

function getCookie(name){
	return localStorage.getItem(name)
}

////////////////////////////////////////////////////////////////////////////////////////////////
//			document.getElementById('body').innerHTML=i


window.addEventListener('scroll',onscroll)
window.addEventListener('DOMContentLoaded', onload)


posts=[]
shownposts=[]
body=0
start=0
postsinpage=32
scrpix=0

function onscroll(){
	scrpix=Math.round(window.scrollY)
	newposts=getoverpage()
	if (newposts!=null){
		newposts-=start
		for (i=start+postsinpage;i<start+newposts+postsinpage&&i<posts.length;i++){
			if (posts[i].posted==0){
				body.innerHTML+=posttotext(posts[i])
				posts[i].posted=1
			}
		}
		for (i=start;i<start+newposts&&i<posts.length;i++){
//					document.getElementById('_'+i).parentNode.removeChild(document.getElementById('_'+i))
		}
		start+=newposts
		if (start>posts.length){
			start=posts.length
		}
		setCookie('start',posts[start].orig)
	}
}

function getoverpage(st=null,fi=null){
	if (st==null){
		st=start
	}
	if (fi==null){
		fi=start+postsinpage
	}
	if (fi>posts.length){
		fi=posts.length
	}
	if (posts.length==0){
		console.log('len=0')
		return
	}
	if (document.getElementById('_'+st).getBoundingClientRect().bottom>=0){
		return
	}
	if (fi<=st){
		console.log('len<0')
		return
	}
	if (fi-st==1){
		return st
	}
	ce=Math.round((fi+st)/2)
	if (document.getElementById('_'+ce).getBoundingClientRect().bottom<0){
		return getoverpage(ce,fi)
	}
	return getoverpage(st,ce)
}

function posttotext(q){
	text='<div class=post id=_'+q.index+'><br><h3>'+q.public+'</h3><h5>'+q.text+'</h5><br>'
	for (photo of q.photos){
		text+='<img src='+photo+' width="100%"><br>'
	}
	text+='\n<div class="orig"><h3><a target="_blank" href=https://vk.com/wall'+q.orig+'><img height="64px" src=orig.png width="64px"></a></h3></div></div>\n'
	return text
}

function up(){
	setCookie('up','1')
	document.location.reload()
}

function onload(){
	body=document.getElementById('body')
	fetch('/json').then(function(r) {
		r.json().then(function(json){
			posts=json
			start=0
			cs=getCookie('start')
			i=0
			if (getCookie('up')=='1'){
				setCookie('up','0')
				cs=null
			}
			for (post of posts){
				post.index=i
				post.posted=0
				if (cs==post.orig){
					start=i
				}
				i++
			}
			body.innerHTML=''
			for (i=start;i<posts.length&&i<postsinpage+start;i++){
				body.innerHTML+=posttotext(posts[i])
				posts[i].posted=1
			}
		})
	})
		}
