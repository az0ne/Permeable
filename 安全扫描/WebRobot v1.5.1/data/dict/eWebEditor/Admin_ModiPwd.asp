<!--#include file = "Include/Startup.asp"-->
<!--#include file = "Include/md5.asp"-->
<!--#include file = "admin_private.asp"-->
<%
'������������������������������������
'��                                                                  ��
'��                eWebEditor - eWebSoft���߱༭��                   ��
'��                                                                  ��
'��  ��Ȩ����: eWebSoft.com                                          ��
'��                                                                  ��
'��  ��������: eWeb�����Ŷ�                                          ��
'��            email:webmaster@webasp.net                            ��
'��            QQ:589808                                             ��
'��                                                                  ��
'��  �����ַ: [��Ʒ����]http://www.eWebSoft.com/Product/eWebEditor/ ��
'��            [֧����̳]http://bbs.eWebSoft.com/                    ��
'��                                                                  ��
'��  ��ҳ��ַ: http://www.eWebSoft.com/   eWebSoft�ŶӼ���Ʒ         ��
'��            http://www.webasp.net/     WEB������Ӧ����Դ��վ      ��
'��            http://bbs.webasp.net/     WEB����������̳            ��
'��                                                                  ��
'������������������������������������
%>

<%

sPosition = sPosition & "�޸��û���������"

Call Header()
Call Content()
Call Footer()


Sub Content()
	Select Case sAction
	Case "MODI"
		' �޸Ĳ���
		Call DoModi()
	Case Else
		' �޸ı�
		Call ShowForm()
	End Select
End Sub

' ��ʾ�޸ı�
Sub ShowForm()
%>
<script language=javascript>
// �ͻ�����֤������Ч��
function checklogin() {
	var obj;
	obj=document.myform.newusr;
	obj.value=BaseTrim(obj.value);
	if (obj.value=="") {
		BaseAlert(obj, "���û�������Ϊ�գ�");
		return false;
	}
	obj=document.myform.newpwd1;
	obj.value=BaseTrim(obj.value);
	if (obj.value=="") {
		BaseAlert(obj, "�����벻��Ϊ�գ�");
		return false;
	}
	if (document.myform.newpwd1.value!=document.myform.newpwd2.value){
		BaseAlert(document.myform.newpwd1, "�������ȷ�����벻��ͬ��");
		return false;
	}
	return true;
}
</script>

<br>
<table border=0 cellpadding=0 cellspacing=0 align=center class=form1>
<form action='?action=modi' method=post name=myform onsubmit="return checklogin()">
<tr><th>&nbsp;&nbsp;�޸����ĵ�¼�û������루ÿ����</th></tr>
<tr><td>���û�����<input type=text class=input size=20 name=newusr value="<%=inHTML(Session("eWebEditor_User"))%>">&nbsp;&nbsp;���û�����<span class=highlight1><%=outHTML(Session("eWebEditor_User"))%></span></td></tr>
<tr><td>�� �� �룺<input type=password class=input size=20 name=newpwd1 maxlength=30>&nbsp;&nbsp;ȷ�����룺<input type=password class=input size=20 name=newpwd2 maxlength=30></td></tr>
<tr><td align=center><input type=image border=0 src='admin/submit.gif' align=absmiddle>&nbsp;<a href='javascript:document.myform.reset()'><img border=0 src='admin/reset.gif' align=absmiddle></a></td></tr>
</form>
</table>
<br><br>

<%
End Sub

' �޸Ĳ���
Sub DoModi()
	' ����������֤������Ч��
	If IsSelfRefer() = False Then
		Go_Error "�ύ�������⣡����"
	End If

	Dim sNewUsr, sNewPwd1, sNewPwd2
	sNewUsr = Trim(Request("newusr"))
	sNewPwd1 = Trim(Request("newpwd1"))
	sNewPwd2 = Trim(Request("newpwd2"))

	If sNewUsr = "" Then
		Go_Error "���û�������Ϊ�գ�"
	End If
	If sNewPwd1 = "" then
		Go_Error "�����벻��Ϊ�գ�"
	End If
	If sNewPwd1 <> sNewPwd2 Then
		Go_Error "�������ȷ�����벻��ͬ��"
	End If

	sSql = "select * from ewebeditor_system"
	oRs.Open sSql, oConn, 1, 3
	If Not oRs.Eof Then
		oRs("sys_username") = md5(sNewUsr)
		oRs("sys_userpass") = md5(sNewPwd1)
		oRs.Update
	End If
	oRs.Close

	Response.Write "<br><p align=center class=title>�޸��û���������</p>" & _
		"<br><table border=0 cellspacing=20 align=center>" & _
		"<tr valign=top><td><img src='admin/do_ok.gif' border=0></td><td><b><span class=highlight2>��¼�û����������޸ĳɹ���</span></b><br><br><ul>������<br><br><li><a href='admin_default.asp'>���غ�̨������ҳ</a><li><a href='admin_modipwd.asp'>�����޸�</a></ul></td></tr>" & _
		"</table><br><br>"

End Sub

%>