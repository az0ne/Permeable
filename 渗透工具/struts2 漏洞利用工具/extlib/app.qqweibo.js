/****************************
//[[Description:QQ΢�����Žӿ�]]
//[[Author: gainover]]
****************************/
/*
2011-7-12
appname:		Ӧ�ó�������
appkey:			Ӧ��key (��΢���ٷ��ṩ)
appsecret:		Ӧ��secret (��΢���ٷ��ṩ)
mainFunc:		��¼��Ϻ���ָ��Ļص�����
url:			�Զ���Ȩ������ת�ĵ�ַ (���Ƽ�ʹ��)
auth_div_id:	��ʾ��Ȩ������div (Ĭ��Ϊ��,���Ƽ��Լ���д)
*/
$Q("App");
//require
$D("coder.base64",true);
$D("coder.sha1",true);

$D("app.qqweibo");

App.qqWeibo=App.qqweibo=App.QQweibo=_QQweibo;

_QQweibo.REQ_COUNT=0;

function _QQweibo(appname,appkey,appsecret,mainFunc,url,auth_div_id){
	var that=this;
	this.hostname="qqweibo";
	this.appname=appname||"�µ�΢��Ӧ��";
	this.appkey=appkey||"";
	this.appsecret=appsecret||"";
	this.token="";
	this.tokensecret="";
	this.verifier="";
	/*----------------------------------------------------*/
	this.debug=false;			//�Ƿ����õ���ģʽ
	this.url=url||location.href;
	this.callback="http://open.t.qq.com/images/resource/p9.gif"; //callback��ַ
	this.callback_ok=false;		//��¼callback״̬
	this.name="";
	this.safe=true;				//�Ƿ����õ�¼��ȫģʽ,��Ϊtrue������Ҫ�ֹ�������Ȩ��
	this.loadingShowed=false;
	this.userflag="";			//���ڶ��û�Ӧ��,��Ϊ�û��ı�ʶ��
	this.main=function(){
		if(mainFunc&&$Y(mainFunc)=="function"){
			mainFunc.apply(this);
		}
	};
	this.auth_param={
		"id":auth_div_id||"toolmao_auth_div"
	};
	this.logo={
		"big":"",
		"bgcolor":"#128ABC",
		"small":"",
		"ok":"",
		"okover":"",
		"verifier":"",
		"help":"",
		"code":"",
		"codeover":""
	};
	this.login_Status=function(){
		//��ȫģʽ
		var __record=that.read_Token();
		if(__record){
			//˵���Ѿ��洢��
			that.token=__record["token"];
			that.tokensecret=__record["tokensecret"];
			that.name=__record["name"];
			//alert("��¼���");
			if(that.main){
				that.main();
			}
			return true;
		}else{
			return false;
		}
	};
	this.write_Token=function(obj){
		var dir=Win.path()+"token";
		if(!Dir.exists(dir)){
			Dir.add(dir);
			Dir.add(dir+"\\"+this.hostname);
		}else{
			if(!Dir.exists(dir+"\\"+this.hostname)){
				Dir.add(dir+"\\"+this.hostname);
			}
		}
		var f=File.open(Win.path()+"token\\"+this.hostname+"\\tokens"+(this.userflag||""));
		File.write(f,obj2str(obj),true);
		File.close(f);
	}
	this.read_Token=function(){
		var url=Win.path()+"token\\"+this.hostname+"\\tokens"+(this.userflag||"");
		if(File.exists(url)){
			var f=File.open(url);
			var cont=File.read(f);
			try{
				var obj=str2obj(cont);
				return obj;
			}catch(e){
				return false;
			}
		}else{
			return false;
		}
	}
	this.encode=function(str){
		/*This script fragment from
			����: VILIC VANE
			����: i@vilic.info
			��վ: www.vilic.info
		*/
		return encodeURIComponent(str).replace(/[!\*\(\)']/gi, function (c) {
			var code = c.charCodeAt(0).toString(16).toUpperCase();
			if (code.length == 1) code = "0" + code;
			return "%" + code;
		});
	}
	this.get_Request_Basestring=function(method,url,data){
		var arr=[];
		for(var i in data){
			arr.push(i+"="+data[i]);
		}
		//alert(method.uc()+"&"+encodeURIComponent(url)+"&"+encodeURIComponent(arr.sort().join("&")));
		return method.uc()+"&"+this.encode(url)+"&"+this.encode(arr.sort().join("&"));
	};
	this.get_Request_Basestring2=function(method,url,data){
		var arr=[];
		for(var i in data){
			arr.push(i+"="+this.encode(data[i]));
		}
		//alert(method.uc()+"&"+encodeURIComponent(url)+"&"+encodeURIComponent(arr.sort().join("&")));
		return method.uc()+"&"+this.encode(url)+"&"+this.encode(arr.sort().join("&"));
	};
	this.get_Signature=function(basestring,token){
		var key=encodeURIComponent(that.appsecret)+"&"+(token?encodeURIComponent(token):"");
		return Coder.base64.encode(Coder.sha1.encode(basestring,"str_hmac",key));
	};
	this.get_Query_String=function(data){
		var datastr=[];
		for(var i in data){
			datastr.push(encodeURIComponent(i)+"="+encodeURIComponent(data[i]));
		}
		datastr=datastr.join("&");
		return datastr;
	};
	this.get_Auth_String=function(data){
		var datastr=[];
		for(var i in data){
			datastr.push(encodeURIComponent(i)+"=\""+encodeURIComponent(data[i])+"\"");
		}
		datastr=datastr.join(",");
		return datastr;
	}
	this.parse_Result=function(str){
		var obj={};
		str=str.split("&");
		for(var i=0;i<str.length;i++){
			var tmp=str[i].split("=");
			obj[$T(tmp[0])]=$T(tmp[1]);
		}
		return obj;
	};
	this.build_Data=function(token,verifier,nocallback,add,pic){
		var timestamp=Dom.Random.time("short");
		var rc=_QQweibo.REQ_COUNT++;
		var data={
			"oauth_consumer_key":that.appkey,
			"oauth_signature_method":"HMAC-SHA1",
			"oauth_callback":that.safe?"null":that.callback,
			"oauth_version":"1.0",
			"oauth_nonce":$R(32,"sn"),
			"oauth_timestamp":timestamp
		};
		if(token){
			data["oauth_token"]=token;
		}
		if(verifier){
			data["oauth_verifier"]=verifier;
		}
		if(nocallback){
			delete data["oauth_callback"];
		}
		if(add){
			for(var i in add){
				data[i]=add[i];
			}
		}
		if(data["content"]&&!pic){
			data["content"]=encodeURIComponent(data["content"]);
		}
		return data;
	};
	this.send_Request=function(method,url,data,callback,token,type,pic){
		data=data||{};
		method=(method||"GET").uc();
		var oauth_signature=this.get_Request_Basestring(method,url,data);
		if(pic){
			oauth_signature=this.get_Request_Basestring2(method,url,data);
		}
		data["oauth_signature"]=this.get_Signature(oauth_signature,(token?that.tokensecret:""));//.replace(/\+/g,"%2B").replace(/\//g,"%2F");
			//$("xxx").innerHTML+=(data["oauth_signature"])+"<br/>";
		if(method=="GET"){
			var datastr=this.get_Query_String(data);
			Net.get(url+"?"+datastr,function(rs){
				if(callback){callback(rs);}
			},type,"","","",function(code,r){
				//request failed then show error description
				if(that.debug){
					alert(method+":"+url+":"+r.responseText);
				}else{
					_QQweibo_showError(r.responseText);
				}
			});
		}else if(method=="POST"){
			if(!pic){
				data["oauth_signature"]=this.encode(data["oauth_signature"]);
				Net.post(url,data,function(rs){
					if(callback){callback(rs);}
				},type,"","","",function(code,r){
					//request failed then show error description
					if(that.debug){
						alert(method+":"+url+":"+r.responseText);
					}else{
						_QQweibo_showError(r.responseText);
					}
				});
			}else{
				//var datastr=this.get_Auth_String(data);
				var filedata={};
				//var ext=(File.ext(pic)||"").lc();
				//if(ext=="jpg"){ext="jpeg";}
				filedata["file"]={
					"pic":{
						"path":pic
					}
				};
				filedata["data"]=data;
				filedata["boundary"]=true;
				Net.upload(url,filedata,function(rs){
					if(callback){callback(rs);}
				},type,"","",{
					//"WWW-Authenticate":"OAuth realm=\"www.toolmao.com\","+datastr
				},function(code,r){
					//request failed then show error description
					if(that.debug){
						alert(method+":"+url+":"+r.responseText);
					}else{
						_QQweibo_showError(r.responseText);
					}
				});
			}
		}
	};
	/*��֤������ʾ*/
	this.showLoading=function(){
		if(!Dom.Cookie.read("toolmao_name")){
			this.loadingShowed=true;
			var d=null;
			if($(this.auth_param["id"])){
				//����û������id�Ѿ����ڣ�����ʾ�ڸ�id��
				d=$(this.auth_param["id"]);
			}else{
				d=Dom.Html.add(this.auth_param["id"],"div");
				if(document.body){
					document.body.style.margin="0px";
				}
				d.style.top="0px";
				d.style.left="0px";
			}
			d.style.position="absolute";
			d.style.width="100%";
			d.style.height="100%";
			d.style.background="#f1f1f1";
			d.style.textAlign="center";
			d.style.fontSize="12px";
			d.innerHTML="<div style='background:"+that.logo.bgcolor+";text-align:center;height:92px;line-height:92px;font-size:36px;'>"+(that.logo.big?("<img src='"+that.logo.big+"' width='252' height='92' />"):that.appname)+"</div><br/><br/><div style='text-align:center;'><img src='"+that.logo.small+"'  onerror='this.style.display=\"none\"'/><br/><br/>���ڼ�����Ѷ΢��������...<br/><br/></div><div style='background:url(#);position:absolute;top:0px;left:0px;width:100%;height:100px;z-index:520;cursor:pointer' id='dragarea'></div>";
			//���ô����϶�����
			Win.Drag.set("dragarea");
		}
	}
	this.showAuthorize=function(){
		var initText="˫����ȡ��Ȩ��";
		var initTextColor="#ccc";
		var url="https://open.t.qq.com/cgi-bin/authorize?oauth_token="+that.token;
		var htmlc="<div style='background:"+that.logo.bgcolor+";text-align:center;height:92px;line-height:92px;font-size:36px;'>"+(that.logo.big?("<img src='"+that.logo.big+"' width='252' height='92' />"):that.appname)+"</div><br/><div style='text-align:center;'><img src='"+that.logo.small+"' onerror='this.style.display=\"none\"'/><br/><br/>��������Ѷ΢����Ȩ��<br/><br/><input type='text' id='toolmao_code_text' style='border:"+(that.logo.code?"none":"1px solid #000")+";background:url("+that.logo.code+") no-repeat;width:105px;height:23px;padding-left:6px;padding-top:4px;color:"+initTextColor+"' value='"+initText+"'/><br/><br/> <input type='button' id='toolmao_ok_button' style='background:url("+that.logo.ok+") no-repeat;width:78px;height:24px;border:"+(that.logo.ok?"none":"1px solid #ccc")+";' value='"+(that.logo.ok?"":"��¼")+"'/><br/></div><div style='position:absolute;bottom:0px;left:0px;text-align:center;'><ul style='text-align:left;width:100%;margin:0px;margin-left:10px;margin-bottom:30px;line-height:2.5;'><li><a href='"+url+"' target='_blank' style='text-decoration:none;height:16px;background:url("+that.logo.verifier+") left center no-repeat;padding-left:20px;'>��˻�ȡ΢����Ȩ��</a></li><li><a href='"+url+"' target='_blank' style='text-decoration:none;height:16px;background:url("+that.logo.help+") left center no-repeat;padding-left:20px;'>ʲô��΢����Ȩ�� ?</a></li></div><div style='background:url(#);position:absolute;top:0px;left:0px;width:100%;height:100px;z-index:520;cursor:pointer' id='dragarea'></div>";
		var d=null;
		if($(this.auth_param["id"])){
			//����û������id�Ѿ����ڣ�����ʾ�ڸ�id��
			d=$(this.auth_param["id"]);
		}else{
			d=Dom.Html.add(this.auth_param["id"],"div");
			if(document.body){
				document.body.style.margin="0px";
			}
			d.style.top="0px";
			d.style.left="0px";
		}
		d.style.position="absolute";
		d.style.width="100%";
		d.style.height="100%";
		d.style.background="#f1f1f1";
		d.style.textAlign="center";
		d.style.fontSize="12px";
		d.innerHTML=htmlc;
		d.style.display="";
		//���ô����϶�����
		Win.Drag.set("dragarea");
		if($("toolmao_ok_button")){
			$("toolmao_ok_button").onclick=function(){
				if($('toolmao_code_text').value!=""&&$('toolmao_code_text').value!=initText){
					that.verifier=$T($('toolmao_code_text').value);
					that.get_Access_Token();
				}else{
					alert("��������Ȩ��");
				}
			};
			$("toolmao_ok_button").onmouseover=function(){
				this.style.background="url("+that.logo.okover+") no-repeat";
			};
			$("toolmao_ok_button").onmouseout=function(){
				this.style.background="url("+that.logo.ok+") no-repeat";
			};
		}
		if($("toolmao_code_text")){
			$("toolmao_code_text").onblur=function(){
				if(this.value==""){
					this.value=initText;
					this.style.color=initTextColor;
					this.style.background="url("+that.logo.code+") no-repeat";
				}
			};
			$("toolmao_code_text").onfocus=function(){
				if(this.value==initText){
					this.value="";
					this.style.color="#000";
					this.style.background="url("+that.logo.codeover+") no-repeat";
				}
			};
			$("toolmao_code_text").ondblclick=function(){
				window.open(url);
			};
		}
	}
	/*��֤���ֺ���*/
	this.get_Request_Token=function(callback){
		this.send_Request("GET","https://open.t.qq.com/cgi-bin/request_token",that.build_Data(),function(rs){
			if(rs){
				var data=that.parse_Result(rs);
				//�ص�
				if(callback){callback(data);}
				//oauth_token
				//oauth_token_secret
				//oauth_callback_confirmed
				that.token=data["oauth_token"];
				that.tokensecret=data["oauth_token_secret"];
				that.showAuthorize();
				//Dom.Cookie.write("tokensecret",that.tokensecret);
				//that.callback_ok=(data["oauth_callback_confirmed"]=="true"?true:false);
				//��ȡ����֮�󣬽����û���֤
				//if(!Dom.Cookie.read("toolmao_name")){

				/*}else{
					that.token=Dom.Cookie.read("oauth_token");
					that.tokensecret=Dom.Cookie.read("oauth_token_secret");
					that.name=Dom.Cookie.read("name");
					if(that.main){
						that.main();
					}
				}*/
			}else{
				_QQweibo_showError(1);
			}
		});
	}
	this.get_Access_Token=function(){
		$("toolmao_ok_button").value="��¼��..";
		$("toolmao_code_text").value="0��"
		var tmpt=Dom.Timer.start(function(){
			$("toolmao_code_text").value=($P($("toolmao_code_text").value)+1)+"��";
		},1000);
		this.send_Request("GET","https://open.t.qq.com/cgi-bin/access_token",that.build_Data(that.token,that.verifier,true),function(rs){
			if(rs){
				Dom.Timer.stop(tmpt);
				var data=that.parse_Result(rs);
				that.token=data["oauth_token"];
				that.tokensecret=data["oauth_token_secret"];
				that.name=data["name"];
				that.write_Token({
					"token":that.token,
					"tokensecret":that.tokensecret,
					"name":that.name
				});
				if(that.safe){
					//���ص�¼����
					$(that.auth_param["id"]).style.display="none";
					if(that.main){
						that.main();
					}
				}else{

				}
			}
		},true);
	}
	this.login=function(func){
		this.showLoading();
		this.start(func);
	}
	this.request=function(url,method,data,callback,format,pic){
		format=format||"json";
		that.send_Request(method,url,that.build_Data(that.token,that.verifier,true,data),function(rs){
			if(callback){
				callback(rs);
			}
		},true,format,pic);
	}
	this.get=function(url,data,callback,format,pic){
		this.request(url,"get",data,callback,format,pic);
	}
	this.post=function(url,data,callback,format,pic){
		this.request(url,"post",data,callback,format,pic);
	}
	/*QQ΢�����еĺ���*/
	this.Timeline={
		//�ҵ���ҳ
		_home:function(callback,format,pageflag,pagetime,reqnum){
			reqnum=reqnum||20; //��ȡ���������
			pageflag=pageflag||0; //
			pagetime=pagetime||0;
			format=format||"json";
			var url="http://open.t.qq.com/api/statuses/home_timeline";
			that.send_Request("GET",url,that.build_Data(that.token,that.verifier,true,{
				format:format,
				pageflag:pageflag,
				reqnum:reqnum,
				pagetime:pagetime
			}),function(rs){
				if(callback){
					callback(rs);
				}
			},true,format);
		},
		//΢������
		_public:function(callback,format,pos,reqnum){
			format=format||"json";
			pos=pos||0;
			reqnum=reqnum||20;
			var url="http://open.t.qq.com/api/statuses/public_timeline";
			that.send_Request("GET",url,that.build_Data(that.token,that.verifier,true,{
				format:format,
				pos:pos,
				reqnum:reqnum
			}),function(rs){
				if(callback){
					callback(rs);
				}
			},true,format);
		},
		//�û�
		_user:function(callback,format,pageflag,pagetime,reqnum,name){
			reqnum=reqnum||20; //��ȡ���������
			pageflag=pageflag||0; //
			pagetime=pagetime||0;
			format=format||"json";
			var sobj={
				format:format,
				pageflag:pageflag,
				reqnum:reqnum,
				pagetime:pagetime
			};
			if(name){
				sobj.name=name;
			}
			var url="http://open.t.qq.com/api/statuses/user_timeline";
			that.send_Request("GET",url,that.build_Data(that.token,that.verifier,true,sobj),function(rs){
				if(callback){
					callback(rs);
				}
			},true,format);
		},
		//�ᵽ�ҵ�
		_mention:function(callback,format,pageflag,pagetime,reqnum,lastid){
			reqnum=reqnum||20; //��ȡ���������
			pageflag=pageflag||0; //
			pagetime=pagetime||0;
			format=format||"json";
			var sobj={
				format:format,
				pageflag:pageflag,
				reqnum:reqnum,
				pagetime:pagetime
			};
			if(lastid){
				sobj.lastid=lastid;
			}
			var url="http://open.t.qq.com/api/statuses/mentions_timeline";
			that.send_Request("GET",url,that.build_Data(that.token,that.verifier,true,sobj),function(rs){
				if(callback){
					callback(rs);
				}
			},true,format);
		},
		//����
		_topic:function(callback,format,httext,pageflag,pageinfo,reqnum){
			reqnum=reqnum||20; //��ȡ���������
			pageflag=pageflag||0; //
			pageinfo=pageinfo||"";
			format=format||"json";
			var sobj={
				format:format,
				pageflag:pageflag,
				reqnum:reqnum,
				pagetime:pagetime
			};
			if(httext){
				sobj.httext=httext;
			}
			var url="http://open.t.qq.com/api/statuses/ht_timeline";
			that.send_Request("GET",url,that.build_Data(that.token,that.verifier,true,sobj),function(rs){
				if(callback){
					callback(rs);
				}
			},true,format);
		},
		//�ҵĹ㲥
		_broadcast:function(callback,format,pageflag,pagetime,reqnum,name){
			reqnum=reqnum||20; //��ȡ���������
			pageflag=pageflag||0; //
			pagetime=pagetime||0;
			format=format||"json";
			var sobj={
				format:format,
				pageflag:pageflag,
				reqnum:reqnum,
				pagetime:pagetime
			};
			if(name){
				sobj.name=name;
			}
			var url="http://open.t.qq.com/api/statuses/broadcast_timeline";
			that.send_Request("GET",url,that.build_Data(that.token,that.verifier,true,sobj),function(rs){
				if(callback){
					callback(rs);
				}
			},true,format);
		},
		_me:this._broadcast
	}
	this.Weibo={
		//��ȡһ��΢��������
		show:function(callback,format,id){
			id=id||"";
			format=format||"json";
			var sobj={
				format:format,
				id:id
			};
			if(id){
				var url="http://open.t.qq.com/api/t/show";
				that.send_Request("GET",url,that.build_Data(that.token,that.verifier,true,sobj),function(rs){
					if(callback){
						callback(rs);
					}
				},true,format);
			}else{
				_QQweibo_showError(3);
			}
		},
		//����һ��΢��
		add:function(callback,format,content,clientip,jing,wei){
			format=format||"json";
			clientip=clientip||"127.0.0.1";
			jing=jing||"";
			wei=wei||"";
			var sobj={
				format:format,
				clientip:clientip,
				jing:jing,
				wei:wei,
				content:content
			};
			if(content){
				var url="http://open.t.qq.com/api/t/add";
				that.send_Request("POST",url,that.build_Data(that.token,that.verifier,true,sobj),function(rs){
					if(callback){
						callback(rs);
					}
				},true,format);
			}else{
				_QQweibo_showError(4);
			}
		},
		//ɾ��һ��΢��
		del:function(callback,format,id){
			format=format||"json";
			id=id||"";
			var sobj={
				format:format,
				id:id
			};
			if(id){
				var url="http://open.t.qq.com/api/t/del";
				that.send_Request("POST",url,that.build_Data(that.token,that.verifier,true,sobj),function(rs){
					if(callback){
						callback(rs);
					}
				},true,format);
			}else{
				_QQweibo_showError(5);
			}
		},
		//ת��һ��΢��
		tui:function(callback,format,content,clientip,jing,wei,reid){
			format=format||"json";
			clientip=clientip||"127.0.0.1";
			jing=jing||"";
			wei=wei||"";
			if(!reid){
				_QQweibo_showError(6);
				return false;
			}
			var sobj={
				format:format,
				clientip:clientip,
				jing:jing,
				wei:wei,
				content:content,
				reid:reid
			};
			//ת����������Ϊ��
			var url="http://open.t.qq.com/api/t/re_add";
			that.send_Request("POST",url,that.build_Data(that.token,that.verifier,true,sobj),function(rs){
				if(callback){
					callback(rs);
				}
			},true,format);
		},
		//�ظ�һ��΢��
		reply:function(callback,format,content,clientip,jing,wei,reid){
			format=format||"json";
			clientip=clientip||"127.0.0.1";
			jing=jing||"";
			wei=wei||"";
			if(!reid){
				_QQweibo_showError(8);
				return false;
			}
			var sobj={
				format:format,
				clientip:clientip,
				jing:jing,
				wei:wei,
				content:content,
				reid:reid
			};
			if(content){
				var url="http://open.t.qq.com/api/t/reply";
				that.send_Request("POST",url,that.build_Data(that.token,that.verifier,true,sobj),function(rs){
					if(callback){
						callback(rs);
					}
				},true,format);
			}else{
				_QQweibo_showError(7);
			}
		},
		//������ͼƬ��΢��
		pic:function(callback,format,content,clientip,jing,wei,pic){
			format=format||"json";
			clientip=clientip||"127.0.0.1";
			jing=jing||"";
			wei=wei||"";
			var sobj={
				format:format,
				clientip:clientip,
				content:content,
				jing:jing,
				wei:wei
			};
			if(pic){
				var url="http://open.t.qq.com/api/t/add_pic";
				that.send_Request("POST",url,that.build_Data(that.token,that.verifier,true,sobj,true),function(rs){
					if(callback){
						callback(rs);
					}
				},true,format,pic);
			}else{
				_QQweibo_showError(9);
			}
		},
		//��ȡ΢��ת������
		count:function(callback,format,ids){
			format=format||"json";
			if($Y(ids)=="array"){
				ids=ids.join(",");
			}
			var sobj={
				format:"json",
				ids:ids
			};
			if(ids){
				var url="http://open.t.qq.com/api/t/re_count";
				that.send_Request("GET",url,that.build_Data(that.token,that.verifier,true,sobj),function(rs){
					if(callback){
						callback(rs);
					}
				},true,format);
			}else{
				_QQweibo_showError(10);
			}
		},
		//��ȡ����΢����ת��/�����б�
		list:function(callback,format,rootid,pageflag,pagetime){
			format=format||"json";
			pageflag=pageflag||0;
			pagetime=pagetime||0;
			var sobj={
				format:format,
				pageflag:pageflag,
				pagetime:pagetime,
				rootid:rootid
			};
			if(rootid){
				var url="http://open.t.qq.com/api/t/re_list";
				that.send_Request("GET",url,that.build_Data(that.token,that.verifier,true,sobj),function(rs){
					if(callback){
						callback(rs);
					}
				},true,format);
			}else{
				_QQweibo_showError(11);
			}
		},
		error:function(n){
			return _QQweibo_msg(n);
		}
	}
	this.ok=this.login_Status;
	this.start=this.get_Request_Token;
	this.load=function(){
		if(!this.ok()){
			this.showLoading();
			this.start();
		}
	};
}

function _QQweibo_showError(n){
	n=$T(n||"noinfo");
	var WeiboError={
		"1":"�����ӷ������޷�����Request Token����",
		"2":"δ��ȡtoken֮ǰ�޷�������֤",
		"3":"Weibo.show����ȱ�ٱ�Ҫ�Ĳ���id",
		"4":"Weibo.add����ȱ�ٱ�Ҫ�Ĳ���content",
		"5":"Weibo.del����ȱ�ٱ�Ҫ�Ĳ���id",
		"6":"Weibo.tui����ȱ����Ҫ�Ĳ���reid",
		"7":"Weibo.reply����ȱ�ٱ�Ҫ�Ĳ���content",
		"8":"Weibo.reply����ȱ����Ҫ�Ĳ���reid",
		"9":"Weibo.pic����ȱ����Ҫ�Ĳ���pic",
		"10":"Weibo.count����ȱ����Ҫ�Ĳ���ids",
		"11":"Weibo.list����ȱ�ٱ�Ҫ�Ĳ���rootid",
		"Invalid / expired Token":"�����������Ȩ����Ч",
		"access rate limit":"ÿ���ӷ��ʴ�����������",
		"noinfo":"δ֪����"
	}
	alert(WeiboError[n]||n);
}
function _QQweibo_msg(n){
	return (["�ɹ�","�ļ���С����","","","�й����໰","��ֹ����:����У�uin���������Ƶ�","ɾ��ʱ���ü�¼�����ڡ�����ʱ�����ڵ��Ѳ�����","","���ݳ�����󳤶ȣ�420�ֽ�","����������Ϣ����棬�������ӡ������������","����̫�죬��Ƶ������","Դ��Ϣ��ɾ������ת����ظ�ʱ","Դ��Ϣ�����","�ظ�����"][$P(n)])||"";
}
/**
//Sample

	var myw=new App.QQweibo("΢�����","4a2ee50d1f8c4f6xx97cc1f8c8fc7d1bf","eaed027xxxxd42ec9f31dc5958ad6cba","");
	//����һ���µ�QQ΢����������Ϊ  myw,
	//���У��������α�ʾ�� Ӧ�����ƣ� Appkey, Appsecret , �ص���ַ ...

	myw.main=function(){
		//�������д�Ĵ��룬�ǵ��û���¼�ɹ��󣬻�ִ�еĴ���
		myw.get("http://open.t.qq.com/api/user/info",{
			"format":"json"
		},function(rs){
			if(rs&&rs.data){
			 alert("��ȡ������Ϣ�ɹ�");
			}
		});
		//������ ΢������� get �÷��� ���������ǣ� �����ַ���������ݸ�ʽ����������
	};

	// ���������Ĳ���֮�󣬾Ϳ��Կ�ʼ���û���¼΢���ˡ�

	if(!myw.ok()){ // myw.ok() �����ж��û��Ƿ��ѵ�¼������ѵ�¼���򷵻�true, ���򷵻� false
		//����û�û��¼����ִ�����²���
		//��ʾ������
		myw.showLoading();
		//��ʼ����
		myw.start();
	}
	//alternative method "load()" in one line
	//myw.load()
*/
