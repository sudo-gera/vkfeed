
function len(q){
	return q.length
}

function print(...q){
	console.log(q)
}
printc=console.log

function get_post(i){
	return document.getElementById('_'+i)
}

function del_post(i){
	get_post(i).parentNode.removeChild(get_post(i))
}


function url_creator(post){
	return post.date+post.orig
}


function post_to_text(q){
	q=globals.posts[q]
	urlopen('/post/'+q.url,(json)=>{
		st=0
		fi=globals.posts.length-1
		while (fi-st>1){
			ce=Math.round((fi+st)/2)
			if (globals.posts[ce].url>url_creator(json)){
					st=ce
			}
			if (globals.posts[ce].url<url_creator(json)){
				fi=ce
			}
			if (globals.posts[ce].url==url_creator(json)){
				fi=ce
				st=ce
			}
		}
		if (globals.posts[fi].url==url_creator(json)){
			st=fi
		}
		q=json
		text='<br><h1>'+q.public+'</h1><h3>'+q.text+'</h3><br>'
		for (photo of q.photos){
			text+='\n<img src="data:image/png;base64,'+photo+' "width="100%"><br>'
		}
		text+='\n<div class="orig"><h3><a target="_blank" href=https://vk.com/wall'+q.orig+'><img height="64px" src=orig.png width="64px"></a></h3></div>'
		get_post(st).innerHTML=text
	})
	text='<div class=post id=_'+q.index+'>'+'<br/>'.repeat(10)+'</div>\n'
	return text
}


function urlopen(url,f){
	fetch(url).then((r)=>{r.json().then(f)})
}

////////////////////////////////////////////////////////////////////////////////////////////////




globals=Object()
globals.posts_in_page=8
globals.posts_edge=4




function get_first_showed(){
	if (globals.first_posted!=undefined && globals.first_not_posted!=undefined){
		for (post_index=globals.first_posted;post_index<globals.first_not_posted;++post_index){
			if (get_post(post_index).getBoundingClientRect().bottom>=0 && get_post(post_index).getBoundingClientRect().top<=0){
				return post_index
			}
		}
		for (post_index=globals.first_posted;post_index<globals.first_not_posted;++post_index){
			if (get_post(post_index).getBoundingClientRect().bottom>=0 && get_post(post_index).getBoundingClientRect().top>0){
				return post_index
			}
		}
		return globals.first_posted
	}
}


function show_post(i){
	if (i<0 || i>len(globals.posts)-1){
		printc('show post error: out of range: '+i)
		return
	}
	if (globals.posts[i].posted){
		printc('show post error: posted==1: '+i)
		return
	}
	if (globals.first_showed<i){
		body.innerHTML+=post_to_text(i)
	}else{
		body.innerHTML=post_to_text(i)+body.innerHTML
	}
	globals.posts[i].posted=1
}

function hide_post(i){
	if (i<0 || i>len(globals.posts)-1){
		printc('hide post error: out of range: '+i)
		return
	}
	if (globals.posts[i].posted==0){
		printc('hide post error: posted==0 '+i)
		return
	}
	body.removeChild(get_post(i))
	globals.posts[i].posted=0
}


setInterval(update_ui,2000)
function update_ui(){
	globals.first_showed=get_first_showed()
	if (globals.first_showed==null || globals.first_showed==undefined){
		return
	}
	for (first_posted=globals.first_showed;first_posted>=0 && globals.posts[first_posted].posted==1;--first_posted){}
	first_posted+=1
	for(first_not_posted=globals.first_showed;first_not_posted<=len(globals.posts)-1 && globals.posts[first_not_posted].posted==1;++first_not_posted){}

	bot1=get_post(globals.first_showed).getBoundingClientRect().bottom
	for (;first_posted<len(global.posts) && first_posted<globals.first_showed-globals.posts_edge;++first_posted){
		hide_post(first_posted);
	}
	for (;first_posted>0 && first_posted>globals.first_showed-globals.posts_edge;--first_posted){
		show_post(first_posted-1);
	}
	for (;first_not_posted<len(global.posts) && first_not_posted<globals.first_showed+globals.posts_in_page+globals.posts_edge;++first_not_posted){
		show_post(first_not_posted);
	}
	for (;first_posted>0 && first_not_posted>globals.first_showed+globals.posts_in_page+globals.posts_edge;--first_not_posted){
		hide_post(first_not_posted-1);
	}
	bot2=get_post(globals.first_showed).getBoundingClientRect().bottom
	window.scrollBy(0,-bot1+bot2)

	globals.first_posted=first_posted
	globals.first_not_posted=first_not_posted
	localStorage.setItem('first_posted',globals.posts[globals.first_posted+globals.posts_edge].url)

}






window.addEventListener('DOMContentLoaded', onload)
function onload(){
	globals.upbutton=document.getElementById('upbutton')
	globals.upbutton.addEventListener('click',up)
	globals.body=document.getElementById('body')
	urlopen('json',(json)=>{
		globals.posts=json
		globals.first_posted=0
		first_posted=localStorage.getItem('first_posted')
		if (localStorage.getItem('up')=='1'){
			localStorage.setItem('up','0')
			first_posted=null
		}
		i=0
		for (post of globals.posts){
			post.index=i
			post.posted=0
			if (first_posted==post.url){
				globals.first_posted=i
			}
			i++
		}
		globals.body.innerHTML=post_to_text(globals.first_posted)
		globals.posts[globals.first_posted].posted=1
		globals.first_not_posted=globals.first_posted+1
		update_ui()
	})
}


function up(){
	localStorage.setItem('up','1')
	document.location.reload()
}
