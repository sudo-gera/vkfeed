var res={};
var q,i;
i=0;
var sf;
sf=Args.sf;
res.items={};
res.items.marked_as_ads=[];
res.items.date=[];
res.items.source_id=[];
res.items.post_id=[];
res.items.text=[];
res.items.attachments=[];
res.items.photos=[];
res.groups={};
res.groups.id=[];
res.groups.name=[];
res.profiles={};
res.profiles.id=[];
res.profiles.first_name=[];
res.profiles.last_name=[];
while (i<25){
	i=i+1;
	q=API.newsfeed.get({"filters":"post","max_photos":100,"count":100,"start_from":sf});
	sf=q.next_from;
	res.items.marked_as_ads=res.items.marked_as_ads+q.items@.marked_as_ads;
	res.items.date=res.items.date+q.items@.date;
	res.items.source_id=res.items.source_id+q.items@.source_id;
	res.items.post_id=res.items.post_id+q.items@.post_id;
	res.items.text=res.items.text+q.items@.text;
	res.items.attachments=res.items.attachments+q.items@.attachments.photos.sizes;
	res.groups.id=res.groups.id+q.groups@.id;
	res.groups.name=res.groups.name+q.groups@.name;
	res.profiles.id=res.profiles.id+q.profiles@.id;

//	items.push([q.items.length]+[q.items@.marked_as_ads]+[q.items@.date]+[q.items@.source_id]+[q.items@.post_id]);
}
//return [sf,items];
return [sf,res];