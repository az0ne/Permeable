<style type="text/css">
<!�C
.STYLE1 {
color: #333333;
font-weight: bold;
}
�C>
</style>
<div align="center"><span>mssql����ű�����
<script language=javascript>
</script>
</span>
<strong>
<script language=javascript></script>
</strong>
<script language=javascript>function checkform()
{
if(form1.filename.value=="")
{
alert("�ļ�������Ϊ��");
history.goback(-1);
}
}
</script>

</div>
<form method=post id=form1>
<div align="center">
<blockquote>
<blockquote> ServerIP:&nbsp;&nbsp;&nbsp;
<input type=text size=20 name=server>
<br>
���ݿ�:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<input type=text size=20 name=dbname>
<br>
�û���:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<input type=text size=20 name=sqluser>
<br>
����:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<input type=text size=20 name=sqlpass>
<br>
����:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<input type=text size=20 name=tablename>
<br>
�����ļ���:&nbsp;
<input type=text size=20 name=filename>
</blockquote>
</blockquote>
<input type=submit value=�ύ onclick=checkform();>
</div>
</form>
<div align="center">
<%
'on error resume next        '������ʾ����
If request("filename")<>"" then
serverip=request("server")
dbname=request("dbname")
sqluser=request("sqluser")
sqlpass=request("sqlpass")
tablename=request("tablename")
SET conn= Server.CreateObject("ADODB.Connection")
conn.open "Provider=SQLOLEDB;Server=" & serverip & ";Database=" & dbname & ";UID=" & sqluser & ";PWD=" & sqlpass        '���ݵ�������
sql="select * from [" & tablename & "]"        'SQL���
set rs=conn.Execute(sql)

set fso=server.CreateObject("Scripting.FileSystemObject")
set file=fso.createtextfile(server.mappath(request("filename")),8,true)

for i=0 to rs.Fields.Count-1
file.write rs(i).name & "###"
next
file.write chr(13) + chr(10)

while not rs.eof
for b=0 to rs.Fields.Count-1
file.write rs(b) & "###"
next
file.write chr(13) + chr(10)
rs.movenext
wend

file.close
set file=nothing
set fso=nothing
conn.Close
End if
%>

</div>
