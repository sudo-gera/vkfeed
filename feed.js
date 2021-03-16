function setCookie(name,value){
	localStorage.setItem(name,value)
}

function getCookie(name){
	return localStorage.getItem(name)
}

////////////////////////////////////////////////////////////////////////////////////////////////
//			document.getElementById('body').innerHTML=i


// window.addEventListener('scroll',onscroll)
window.addEventListener('DOMContentLoaded', onload)


posts=[]
body=0
start=0
postsinpage=8
del=0

function log(q){
	document.getElementById('log').value+=''+q+'\n'
}

function getpost(i){
	return document.getElementById('_'+i)
}

function autodel(){
	statst=start
	op=getpost(statst).getBoundingClientRect().bottom
	for (i=del;i<statst;i++){
		delpost(i)
	}
	del=statst
	window.scrollBy(0,op-getpost(statst).getBoundingClientRect().bottom)
}

setInterval(onscroll,3000)

function delpost(i){
	getpost(i).parentNode.removeChild(getpost(i))
}

function onscroll(){
	newposts=getoverpage()
	if (newposts!=null){
		newposts-=start
		for (i=start+postsinpage;i<start+newposts+postsinpage&&i<posts.length;i++){
			if (posts[i].posted==0){
				body.innerHTML+=posttotext(posts[i])
				posts[i].posted=1
			}
		}
		bot1=getpost(start+newposts).getBoundingClientRect().bottom
		for (i=start;i<start+newposts&&i<posts.length;i++){
			delpost(i)
		}
		bot2=getpost(start+newposts).getBoundingClientRect().bottom
		window.scrollBy(0,-bot1+bot2)
		// alert(bot1+';'+bot2)
		start+=newposts
		if (start>posts.length){
			start=posts.length
		}
		setCookie('start',posts[start].url)
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
	if (getpost(st).getBoundingClientRect().bottom>=0){
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
	if (getpost(ce).getBoundingClientRect().bottom<0){
		return getoverpage(ce,fi)
	}
	return getoverpage(st,ce)
}

function posttotext(q){
	fetch('/post/'+q.url).then(function(r){
		r.json().then(function(json){
			st=0
			fi=posts.length-1
			while (fi-st>1){
				ce=Math.round((fi+st)/2)
				if (posts[ce].url>json.date+json.orig){
					st=ce
				}
				if (posts[ce].url<json.date+json.orig){
					fi=ce
				}
				if (posts[ce].url==json.date+json.orig){
					fi=ce
					st=ce
				}
			}
			if (posts[fi].url==json.date+json.orig){
				st=fi
			}
			q=json
			text='<br><h1>'+q.public+'</h1><h3>'+q.text+'</h3><br>'
			for (photo of q.photos){
				text+='\n<img src="data:image/png;base64,'+photo+' "width="100%"><br>'
			}
			text+='\n<div class="orig"><h3><a target="_blank" href=https://vk.com/wall'+q.orig+'><img height="64px" src=orig.png width="64px"></a></h3></div>'
			getpost(st).innerHTML=text
		})
	})
	text='<div class=post id=_'+q.index+'></div>\n'
	return text
}

function up(){
	setCookie('up','1')
	document.location.reload()
}

function onload(){
	document.getElementById('upbutton').addEventListener('click',up)
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
				if (cs==post.url){
					start=i
				}
				i++
			}
			body.innerHTML=''
			for (i=start;i<posts.length&&i<postsinpage+start;i++){
				body.innerHTML+=posttotext(posts[i])
				posts[i].posted=1
			}
			del=start
		})
	})
}
