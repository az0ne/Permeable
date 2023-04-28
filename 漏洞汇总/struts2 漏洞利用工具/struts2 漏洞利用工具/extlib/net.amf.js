/****************************
//[[Description:Amf���ݲ���]]
//[[Author: gainover]]
****************************/
$Q("Net");

$D("net.amf");
/**
 * Amf���ݴ���
 * @namespace Amf���ݲ���
 */
Net.Amf={
	id:"",
	pageReady:false,
	swfReady:false,
	obj:null,
	callback:null,
	item:0,
	/**
	 * ����һ����ʹ�õ�Amf�������
	 * @param {String} id ����ID
	 * @param {String} [url=""] FLASH�ļ����õ�ַ
	 * @param {Function} [callback=null] �����ɹ���Ļص�����
	 * @returns
	 */
	create:function(id,url,callback,param){
		/*add a window onload event*/
		Dom.Event.add(window,"load",function(){
			Net.Amf.pageReady=true;
		});
		this.id=id;
		if(!param){param={
			"w":0,
			"h":0,
			"t":0,
			"l":0
		};}
		this.callback=callback;
		var str='<object classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000"';
			str+=' id="'+id+'" width="'+param.w+'" height="'+param.h+'"';
			str+=' codebase="http://fpdownload.macromedia.com/get/flashplayer/current/swflash.cab" style="position:absolute;top:'+param.t+'px;left:'+param.l+'px;">';
			str+=' <param name="movie" value="'+(url||external.path+'lib\\use\\Jsamf.swf')+'" />';
			str+=' <param name="quality" value="high" />';
			str+=' <param name="bgcolor" value="#869ca7" />';
			str+=' <param name="allowScriptAccess" value="always" />';
			str+=' <param name="allowNetWorking" value="all" />';
			str+=' <embed src="'+(url||external.path+'lib\\use\\Jsamf.swf')+'" quality="high" bgcolor="#869ca7"';
			str+=' width="0" height="0" name="'+id+'" align="middle"';
			str+=' play="true"';
			str+=' loop="false"';
			str+=' quality="high"';
			str+=' allowScriptAccess="always"';
			str+=' type="application/x-shockwave-flash"';
			str+=' pluginspage="http://www.adobe.com/go/getflashplayer">';
			str+='</embed>';
			str+='</object>';
		document.write(str);
	},
	/**
	 * @ignore
	 * @returns
	 */
	init:function(){
		this.swfReady=true;
		this.obj=document.getElementById(this.id)||window[this.id];
		if(this.callback){this.callback();}
	},
	/**
	 * @ignore
	 * @returns
	 */
	isReady:function(){
		return this.pageReady;
	},
	/**
	 * @ignore
	 * @returns
	 */
	indent:function(i){
		var str="";
		for(var j=0;j<i;j++){
			str+="&nbsp;&nbsp;&nbsp;&nbsp;";
		}
		return str;
	},
	/**
	 * @ignore
	 * @returns
	 */
	show:function(obj,level){
		if(!level){level=1;}
		var str="";
		for(var i in obj){
			this.item++;
			var tp=(typeof obj[i]).toLowerCase();
			if(tp == "object"&&obj[i]){
				str+=this.indent(level)+"<span style='cursor:pointer;display:;' onclick='$(\"item_list_"+this.item+"\").style.display=$(\"item_list_"+this.item+"\").style.display?\"\":\"none\";this.innerHTML=$(\"item_list_"+this.item+"\").style.display?\"+\":\"-\"'>-</span> <B>["+i+"]</B> - <font color='red'><B>"+tp+"</B></font><br/>";
				str+="<div id='item_list_"+this.item+"'>"+this.show(obj[i],level+1)+"</div>";
			}else{
				str+=this.indent(level)+". <B>["+i+"]</B> - <font color='red'><B>"+tp+"</B></font> - "+obj[i]+"<br/>";
			}
		}
		return str;
	}
};
