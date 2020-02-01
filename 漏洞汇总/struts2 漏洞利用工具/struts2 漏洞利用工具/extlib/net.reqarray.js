/****************************
//[[Description:��������]]
//[[Author: gainover]]
****************************/
$Q("Net");

$D("net.reqarray");

Net.__replace_var={};
Net.getvar=function(key){
	return this.__replace_var[key];
}
Net.addvar=function(key,value){
	this.__replace_var[key]=value;
};
Net.delvar=function(key){
	if(key in this.__replace_var){
		delete this.__replace_var[key];
	}
}
Net.updatevar=function(txt,obj){
	if((typeof(txt)+"").lc()=="string"){
		for(var i in obj){
			if(i.substring(0,1)=="!"){
				//json��
				txt=txt.replace(new RegExp("\{"+i+"([\\s\\S]+?)!\}","gi"),function($1,$2){
					return eval("Net.getvar('"+i+"')"+$2);
				});
			}else{
				txt=txt.replace(new RegExp("\{"+i+"\}","gi"),obj[i]);
			}
		}
		txt=txt.replace(/\{cache\}/g,Math.random());
		txt=txt.replace(/\{time\}/g,Dom.Random.time("l"));
		txt=txt.replace(/\{time_short\}/g,Dom.Random.time("s"));
	}else if((typeof(txt)+"").lc()=="object"){
		for(var j in txt){
			for(var i in obj){
				txt[j]=txt[j].replace(new RegExp("\{"+i+"\}","gi"),obj[i]);
				txt[j]=txt[j].replace(/\{cache\}/g,Math.random());
				txt[j]=txt[j].replace(/\{time\}/g,Dom.Random.time("l"));
				txt[j]=txt[j].replace(/\{time_short\}/g,Dom.Random.time("s"));
			}
		}
	}
	return txt;
};
Net.reqarray=function(arr,call,error){
	var that=this;
	var tmp=arr.shift();
	if(tmp){
		function callback (rs){
			if(tmp.capture){
				switch(tmp.type){
					case "json":
						for(var i in tmp.capture){
							that.__replace_var[i]=eval("rs"+tmp.capture[i]);
						}
						break;
					default:
						for(var i in tmp.capture){
							that.__replace_var[i]=rs.getMatch(tmp.capture[i]);
							if(i.substring(0,1)=="!"){
								//ǿ��ת��ΪJSON
								that.__replace_var[i]=str2obj(that.__replace_var[i]);
							}
						}
				}
			}
			var exception=false;
			if(tmp.exception){
				for(var i=0;i<tmp.exception.length;i++){

				}
			}
			Net.reqarray(arr,call);
		}
		function failback(rs){
			if(!fail.ignore){
				if(tmp.fail&&(typeof(tmp.fail)+"").lc=="function"){
					tmp.fail(rs);
				}
				if(error&&(typeof(error)+"").lc() =="function"){
					error(tmp,rs);
				}
			}else{
				Net.reqarray(arr,call);
			}
		}
		if(tmp.method!="GET"){
			Net.post(this.updatevar(tmp.url,this.__replace_var),this.updatevar(tmp.data,this.__replace_var),callback,tmp.type,this.updatevar(tmp.refer,this.__replace_var),tmp.async,this.updatevar(tmp.header,this.__replace_var),failback);
		}else{
			Net.get(this.updatevar(tmp.url,this.__replace_var),callback,tmp.type,this.updatevar(tmp.refer,this.__replace_var),tmp.async,this.updatevar(tmp.header,this.__replace_var),failback);
		}
	}else{
		if(call&&(typeof(call)+"").lc() =="function"){
			call();
		}
	}
};

/*
ʹ��˵��:
1. url���������ַ����������Զ���ģ�����
   {cache} ģ��ᱻ�Զ��滻Ϊ���С��
   {time} ģ��ᱻ�Զ��滻Ϊʱ��
2. method��������ʽ��ȱʡΪPOST
3. data ���巢�����ݣ���������Զ���ģ�����
4. capture ��ʾ���񷵻ؽ���е�����
	a. ������ı������Բ���������ʽ
	b. ���������json, ����ʹ�� ����JS�﷨����ȡ
	c. �����Ҫ����������ַ�����ǿ��ת��ΪJSON�����ڱ���ǰ�� !
5. ignore ��ʾ�������ʱ,���Դ��󣬼���ִ����һ������
6. �Զ���ģ�����
	a. ��ͨģ�壬��ʽΪ {data}, ���������ģ�����������ͨ�� Net.addvar ����ӵı���
	b. Jsonģ��, ��ʽΪ {!data.xxx.yyy!}
7. �����������Net.post��Net.getͬ

var request=[{
	"url":"http://dl.bbs.house.sina.com.cn/forumdisplay.php?fid=59451&hash={cache}&page%3D1",
	"method":"GET",
	"capture":{
		"tmpvar1":/name="formhash" value="(\w{8})"/,
		"tmpvar2":/name="cookietime" value="(\d+)"/,
		"tmpvar3":/name="service" value="(\w+)"/,
		"tmpvar4":/name="returntype" value="(\w+)"/,
		"tmpvar5":/name="savestate" value="(\w+)"/,
		"tmpvar6":/name="loginreferer" value="([^"]+)"/,
		"tmpvar7":/name="myurl" value="([^"]+)"/,
		"tmpvar_typeid":/typeid=(\d+)/
	},
	"type":"charset:gb2312"
},
{
	"url":"http://i.house.sina.com.cn/login_check.php",
	"data":{
		"cookietime":"{tmpvar2}",
		"formhash":"{tmpvar1}",
		"loginfield":"username",
		"loginreferer":"{tmpvar6}",
		"myurl":"{tmpvar7}",
		"name":"{username}",
		"pass":"{password}",
		"remLoginName":"on",
		"returntype":"{tmpvar4}",
		"savestate":"{tmpvar5}",
		"service":"{tmpvar3}"
	},
	"capture":{
		"tmpvar8":/name="password" value="(\w{32})"/,
		"tmpvar9":/name="url" value="([^"]+)"/,
		"tmpvar10":/name="service" value="([^"]+)"/,
		"tmpvar11":/name="useticket" value="(\d+)"/
	},
	"type":"charset:gb2312"
}];
*/