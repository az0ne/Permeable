<!--#include file = "Include/Startup.asp"-->
<!--#include file = "Include/md5.asp"-->
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
' ��ʼ�����ݿ�����
Call DBConnBegin()

Dim sAction, sErrMsg
Dim s_Usr, s_Pwd
sAction = UCase(Trim(Request("action")))
sErrMsg = ""

Select Case sAction
Case "LOGIN"
	s_Usr = Trim(Request("usr"))
	s_Pwd = Trim(Request("pwd"))
	If s_Usr <> "" And s_Pwd <> "" Then
		sSql = "select * from ewebeditor_system"
		oRs.Open sSql, oConn, 0, 1
		If Not oRs.Eof Then
			If oRs("sys_username") = md5(s_Usr) And oRs("sys_userpass") = md5(s_Pwd) Then
				' ��¼�ɹ�
				Session("eWebEditor_User") = s_Usr
				Session("eWebEditor_Version") = oRs("sys_version")
				Response.Redirect "admin_default.asp"
				Response.End
			End If
		End If
		oRs.Close
	End If
	sErrMsg = "��ʾ���û������������"
Case "OUT"
	Session("eWebEditor_User") = ""
End Select

' �ͷ��������Ӷ���
Call DBConnEnd()

%>


<HTML>
<HEAD>
<TITLE>eWebEditor - eWebSoft�����ı��༭�� - ��̨����</TITLE>
<META http-equiv=Content-Type content="text/html; charset=gb2312">
<SCRIPT language=JavaScript>
function checklogin() {
	if (document.myform.usr.value=="") {
		alert("�������û���!");
		myform.usr.focus();
		return false;
	}
	if (document.myform.pwd.value=="") {
		alert("����������!");
		myform.pwd.focus();
		return false;
	}
	return true;
}
</SCRIPT>
<style>
.font {	FONT-SIZE: 9pt; LINE-HEIGHT: 180%; TEXT-DECORATION: none}
.textinput {BORDER-RIGHT: #ffc38c 1px solid; BORDER-TOP: #ffc38c 1px solid; FONT-SIZE: 9pt; BACKGROUND: #ffffff; BORDER-LEFT: #ffc38c 1px solid; BORDER-BOTTOM: #ffc38c 1px solid; FONT-FAMILY: arial}
body,td,input {font-size:9pt}
</style>

</HEAD>
<BODY text=#000000 bgColor=#ff000 leftMargin=0 topMargin=0>

<TABLE height=396 cellSpacing=0 cellPadding=0 width="100%" border=0>
  <TBODY>
  <TR>
    <TD vAlign=top align=middle bgColor=#fffbe7 height=70>&nbsp; </TD></TR>
  <TR>
    <TD vAlign=top align=middle background=admin/login_c2.gif height=163>
      <TABLE cellSpacing=0 cellPadding=0 width=630 border=0>
        <TBODY>
        <TR>
          <TD vAlign=center align=left width=289 height=184 align=center><A href="http://www.ewebsoft.com/"><IMG height=45 src="admin/logo.gif" width=230 border=0></A></TD>
          <TD vAlign=bottom align=middle width=341 background=admin/login_c5.gif height=198>�� �� Ա �� ¼<BR><font color=#0000ff><%=sErrMsg%></font><BR>
            <TABLE cellSpacing=0 cellPadding=0 width=227 border=0>
              <FORM name=myform onsubmit="return checklogin()" action="?action=login" method=post>
              <TBODY>
              <TR vAlign=center>
                <TD class=font align=right width=58 height=32><FONT color=#ff0000>�û�����</FONT></TD>
                <TD width=169><INPUT class=textinput name=usr size=20> </TD>
			  </TR>
              <TR vAlign=center>
                <TD class=font align=right width=58><FONT color=#ff0000>�ܡ��룺</FONT></TD>
                <TD width=169><INPUT class=textinput type=password name=pwd size=20> </TD></TR>
              <TR vAlign=center align=middle>
                <TD colSpan=2 height=46><INPUT type=image height=18 width=35 src="admin/login.gif" border=0 name=imageField></TD>
			  </TR>
			  </FORM>
			  </TBODY>
			</TABLE>
	      </TD>
		</TR>
        <TR>
          <TD vAlign=bottom align=right width=289 height=76><IMG height=74 src="admin/login_c3.gif" width=289></TD>
          <TD vAlign=top align=left width=341 height=76><IMG height=128 src="admin/login_c4.gif" width=314></TD>
		</TR>
		</TBODY>
	  </TABLE>
	</TD>
  </TR>
  </TBODY>
</TABLE>

</BODY>
</HTML>
