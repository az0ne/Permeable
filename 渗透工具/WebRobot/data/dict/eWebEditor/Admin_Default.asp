<!--#include file = "Include/Startup.asp"-->
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

sPosition = ""

Call Header()
Call Content()
Call Footer()


Sub Content()
%>
	<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0 WIDTH="100%">
	<TR><TD ALIGN=right><img border=0 src='admin/logo.gif'></TD></TR>
	<TR><TD ALIGN=center HEIGHT=100><span class=highlight1><b><%=outHTML(Session("eWebEditor_User"))%>����ӭ��ʹ�ñ�ϵͳ</b></span><br><br><br><b><span class=highlight2>Ϊ��֤ϵͳ���ݰ�ȫ��ʹ����������˳���</span></b></TD></TR>
	<TR>
		<TD>
		<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0>
		<TR>
			<TD><B>����汾��</B></TD><TD>eWebEditor Version <%=Session("eWebEditor_Version")%></TD>
		</TR>
		<TR>
			<TD><B>��Ȩ���У�</B></TD><TD>eWebSoft.com</TD>
		</TR>
		<TR>
			<TD><B>����������</B></TD><TD>eWeb�����Ŷ�</TD>
		</TR>
		<TR>
			<TD><B>��ҳ��ַ��</B></TD><TD><a href="http://www.eWebSoft.com" target="_blank">http://www.eWebSoft.com</a>&nbsp;&nbsp;&nbsp;<a href="http://www.webasp.net" target="_blank">http://www.webasp.net</a></TD>
		</TR>
		<TR>
			<TD><B>��Ʒ���ܣ�</B></TD><TD><a href="http://http://www.eWebSoft.com/Product/eWebEditor/" target="_blank">http://www.eWebSoft.com/Product/eWebEditor/</a></TD>
		</TR>
		<TR>
			<TD><B>��̳��ַ��</B></TD><TD><a href="http://bbs.webasp.net" target="_blank">http://bbs.webasp.net</a></TD>
		</TR>
		<TR>
			<TD><B>��ϵ��ʽ��</B></TD><TD>OICQ:589808&nbsp;&nbsp;&nbsp;&nbsp;Email:<a href="mailto:webmaster@webasp.net">webmaster@webasp.net</a></TD>
		</TR>
		</TABLE>
		</TD>
	</TR>
	<TR><TD HEIGHT=30></TD></TR>
	</TABLE>
<%
End Sub
%>