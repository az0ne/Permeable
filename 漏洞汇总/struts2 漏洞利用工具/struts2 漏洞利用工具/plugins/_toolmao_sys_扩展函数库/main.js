var fileBase="";
var server="http://www.toolmao.com/box/ext/";
//var server="http://localhost:8080/extlib/";

function findExt(){
	$("sbutton").disabled=true;
	if($T($("sysbg").innerHTML)!=""){
		$("imglist").innerHTML="<br/>������������..";
		var sstr=$T($("sysbg").innerHTML);
			sstr=sstr.replace(/\.js$/,"");
		Net.post(server+"list.php",{
			"ext":sstr
		},function(rs){
			$("imglist").innerHTML="";
			fileBase=rs.base;
			var d=rs.data;
			if(d.length>0){
				for(var i=0;i<d.length;i++){
					var xx=Dom.Html.add($R(8),"div","imglist");
					xx.innerHTML="<input type='checkbox' id='p_"+i+"' name='extdata' value='"+d[i]+"'></input> <span id='p_"+i+"_st'></span> "+d[i];
				}
			}else{
				$("imglist").innerHTML="<br/>û����ؽ��";
			}
			$("sbutton").disabled=false;
		},"json","","","",function(){
			$("imglist").innerHTML="<br/>�޷����ӵ�������,�����";
			$("sbutton").disabled=false;
		});
	}else{
		alert("������������Ҫ�ĺ���������");
		$("sbutton").disabled=false;
	}
}
var cstat=false;
function selectAll(){
	var ins=document.getElementsByName("extdata");
	cstat=!cstat;
	for(var i=0;i<ins.length;i++){
		ins[i].checked=cstat;
	}
}
function downloadExt(){
	var d=document.getElementsByName("extdata");
	var b=[];
	for(var i=0;i<d.length;i++){
		if(d[i].checked){
			b.push({'url':d[i].value,'id':d[i].id});
		}
	}
	download(b);
}
function download(b){
	if(fileBase){
		var tmp=b.shift();
		if(tmp){
			$(tmp.id+"_st").innerHTML=" [������...]  ";
			Net.get(fileBase+tmp.url+"?hash="+Math.random(),function(rs){
				Stream.saveImage(external.path+"extlib\\"+tmp.url,rs);
				$(tmp.id+"_st").innerHTML=" [���سɹ�]  ";
				download(b);
			},"stream");
		}
	}
}
Dom.Event.add(window,"load",function(){
	$("appData").style.height=($P(parent.document.getElementById("desktop").style.height)-150)+"px";

});
