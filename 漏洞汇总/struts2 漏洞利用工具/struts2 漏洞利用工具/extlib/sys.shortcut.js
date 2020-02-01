/****************************
//[[Description:��ݷ�ʽ����]]
//[[Author: gainover]]
****************************/
$Q("Sys");

Sys.ShortCut={
	link:function(savepath,srcpath,arg,iconpath,desc,workdir,hotkey){
		var wsh=Win.obj(Win.com.WSH);
		var link=wsh.CreateShortcut(savepath);
		link.TargetPath=srcpath;
		link.WindowStyle=1;
		link.Hotkey=hotkey||"";
		link.Description=desc||"��ݷ�ʽ";
		arg&&(link.Arguments=arg);
		workdir&&(link.WorkingDirectory=workdir);
		iconpath&&(link.IconLocation=iconpath);
		link.Save();
		link=null;
		wsh=null;
	},
	url:function(savepath,url){
		if(url){
			var wsh=Win.obj(Win.com.WSH);
			var link=wsh.CreateShortcut(savepath);
			link.TargetPath=url;
			link.Save();
			link=null;
			wsh=null;
		}
	},
	get:function(savepath,attr){
		if(!attr){attr="path";}
		var data={"path":"TargetPath","icon":"IconLocation","wd":"WorkingDirectory","workingdir":"WorkingDirectory","workdir":"WorkingDirectory",
		"Workingdirectory":"WorkingDirectory","desc":"Description","description":"Description","hotkey":"Hotkey","ws":"WindowStyle","windowstyle":"WindowStyle"}[attr]||"TargetPath";
		var wsh=Win.obj(Win.com.WSH);
		var link=wsh.CreateShortcut(savepath);
		var obj="";
		try{
			obj=link[data];
		}catch(e){}
		link=null;
		wsh=null;
		return obj;
	}
};

/*
//ʹ��ʵ��
//��Ӧ�ó��򴴽�һ����ݷ�ʽ
Sys.ShortCut.link(Win.path()+"test.lnk",Win.exe());
//����ַ����һ����ݷ�ʽ
Sys.ShortCut.url(Win.path()+"test.url","http://www.baidu.com");
//���һ����ݷ�ʽ��ԴĿ��
alert(Sys.ShortCut.get(Win.path()+"test.lnk","icon"));
*/
