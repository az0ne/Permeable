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

If Session("eWebEditor_User") = "" Then
	Response.Redirect "admin_login.asp"
	Response.End
End If

' ִ��ÿ��ֻ�账��һ�ε��¼�
Call BrandNewDay()

' ��ʼ�����ݿ�����
Call DBConnBegin()

' ���ñ���
Dim sAction, sPosition
sAction = UCase(Trim(Request.QueryString("action")))
sPosition = "λ�ã�<a href='admin_default.asp'>��̨����</a> / "


' ********************************************
' ����Ϊҳ�湫��������
' ********************************************
' ============================================
' ���ÿҳ���õĶ�������
' ============================================
Sub Header()
	Response.Write "<html><head>"
	
	' ��� meta ���
	Response.Write "<meta http-equiv='Content-Type' content='text/html; charset=gb2312'>" & _
		"<meta name='Author' content='Andy.m'>" & _
		"<link rev=MADE href='mailto:webmaster@webasp.net'>"
	
	' �������
	Response.Write "<title>eWebEditor - eWebSoft�����ı��༭�� - ��̨����</title>"
	
    ' ���ÿҳ��ʹ�õĻ�����ʽ��
	Response.Write "<link rel='stylesheet' type='text/css' href='admin/style.css'>"

	' ���ÿҳ��ʹ�õĻ����ͻ��˽ű�
	Response.Write "<script language='javaScript' SRC='admin/private.js'></SCRIPT>"
	
	Response.Write "</head>"

	Response.Write "<body topmargin=0 leftmargin=0 bgcolor=#ffffff>"
	Response.Write "<a name=top></a>"
	
	' ���ҳ�涥��(Header1)
	Response.Write "<table border=0 cellpadding=0 cellspacing=0 height=41 width=778 align=center class=header1>" & _
		"<tr><td width=170 height=13></td><td width=608 rowspan=2 valign=top>" & _
		"<table border=0 cellpadding=0 cellspacing=0 width='100%'><tr><td height=7></td></tr><tr><td>"
	Response.Write "<table border=0 cellpadding=0 cellspacing=0 width='100%'>" & _
		"<tr>" & _
		"<td width=300></td>" & _
		"<td class=header1><a href='admin_default.asp'>��̨������ҳ</a></td>" & _
		"<td class=header1><a href='admin_login.asp?action=out'>�˳���̨�������ص�¼ҳ</a></td>" & _
		"</tr>" & _
		"</table>"
	Response.Write "</td></tr></table>" & _
		"</td></tr><tr><td width=170 height=19 align=center valign=top>" & Application("date_chinese") & "</td></tr>" & _
		"<tr><td height=9 colspan=2></td></tr>" & _
		"</table>"

	' ҳ���������
	Response.Write "<table border=0 cellpadding=0 cellspacing=0 width=778 align=center>" & _
		"<tr valign=top>" & _
		"<td width=175 class=leftbg>" & _
		"<table border=0 cellpadding=0 cellspacing=0 width='100%' class=lefttext>"
	' ��̨����ģ��
	Call Block_Member()
	Response.Write "</table>" & _
		"</td>" & _
		"<td width=20></td>" & _
		"<td width=575>" & _
		"<table border=0 cellpadding=0 cellspacing=0 width='100%'><tr><td>" & sPosition & "</td></tr><tr><td height=5></td></tr></table>"

End Sub

' ============================================
' ���ÿҳ���õĵײ�����
' ============================================
Sub Footer()
	' �ͷ��������Ӷ���
	Call DBConnEnd()

	Response.Write "</td>"
	Response.Write "<td width=7></td><td width=1 class=rightbg></td>"
	Response.Write "</tr></table>"
	
	' �ײ�����
	Response.Write "<table border=0 cellpadding=0 cellspacing=0 width=778 align=center height=23 class=footer1>" & _
		"<tr valign=bottom>" & _
			"<td>&nbsp;&nbsp;<a href='http://www.webasp.net'><IMG src='admin/c_webasp.gif' border=0></a></td>" & _
			"<td align=right><a href='admin_default.asp' title='��ҳ'><img src='admin/c_dian1.gif' width=15 height=15 border=0></a>��<a href='#top' title='����ҳ��'><img src='admin/c_dian3.gif' width=15 height=15 border=0></a>��<a href='javascript:window.close()' title='�رմ���'><img src='admin/c_dian4.gif' width=15 height=15 border=0></a>&nbsp;&nbsp;</td>" & _
		"</tr>" & _
		"</table>"
	
	Response.Write "<table border=0 cellpadding=0 cellspacing=3 align=center class=footer2>" & _
		"<tr>" & _
			"<td align=center>Copyright  &copy;  2003-2004  <b>webasp<font color=#CC0000>.net</font></b> <b>eWebSoft<font color=#CC0000>.com</font></b>, All Rights Reserved .</td>" & _
		"</tr>" & _
		"<tr>" & _
			"<td align=center><a href='mailto:webmaster@webasp.net'>webmaster@webasp.net</a></td>" & _
		"</tr>" & _
		"</table>"

	Response.Write "</body></html>"
End Sub


' ��̨����ģ��
Sub Block_Member()
	Response.Write "<tr><td align=center>" & _
		"<table class=leftblock border=0 cellpadding=0 cellspacing=0>" & _
		"<tr><th>��̨����</th></tr>" & _
		"<tr><td>" & _
			"<table border=0 cellpadding=0 cellspacing=3 align=center width='100%'>" & _
			"<tr><td>�� <A class=leftnavi href='admin_style.asp'>��ʽ����</a></td></tr>" & _
			"<tr><td>�� <A class=leftnavi href='admin_decode.asp'>��ȡ���ͺ���</a></td></tr>" & _
			"<tr><td>�� <A class=leftnavi href='admin_uploadfile.asp'>�ϴ��ļ�����</a></td></tr>" & _
			"<tr><td>�� <A class=leftnavi href='admin_modipwd.asp'>�û����������޸�</a></td></tr>" & _
			"<tr><td>�� <A class=leftnavi href='admin_login.asp?action=out'>�˳�</a></td></tr>" & _
			"</table>" & _
		"</td></tr>" & _
		"</table>" & _
		"</td></tr>"
End Sub

' ===============================================
' ��ʼ��������
'	s_FieldName	: ���ص���������	
'	a_Name		: ��ֵ������
'	a_Value		: ��ֵֵ����
'	v_InitValue	: ��ʼֵ
'	s_Sql		: �����ݿ���ȡֵʱ,select name,value from table
'	s_AllName	: ��ֵ������,��:"ȫ��","����","Ĭ��"
' ===============================================
Function InitSelect(s_FieldName, a_Name, a_Value, v_InitValue, s_Sql, s_AllName)
	Dim i
	InitSelect = "<select name='" & s_FieldName & "' size=1>"
	If s_AllName <> "" Then
		InitSelect = InitSelect & "<option value=''>" & s_AllName & "</option>"
	End If
	If s_Sql <> "" Then
		oRs.Open s_Sql, oConn, 0, 1
		Do While Not oRs.Eof
			InitSelect = InitSelect & "<option value=""" & inHTML(oRs(1)) & """"
			If oRs(1) = v_InitValue Then
				InitSelect = InitSelect & " selected"
			End If
			InitSelect = InitSelect & ">" & outHTML(oRs(0)) & "</option>"
			oRs.MoveNext
		Loop
		oRs.Close
	Else
		For i = 0 To UBound(a_Name)
			InitSelect = InitSelect & "<option value=""" & inHTML(a_Value(i)) & """"
			If a_Value(i) = v_InitValue Then
				InitSelect = InitSelect & " selected"
			End If
			InitSelect = InitSelect & ">" & outHTML(a_Name(i)) & "</option>"
		Next
	End If
	InitSelect = InitSelect & "</select>"
End Function


%>