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

Dim sStyleID, sStyleName, sStyleDir, sStyleCSS, sStyleUploadDir, sStyleWidth, sStyleHeight, sStyleMemo, nStyleIsSys, sStyleStateFlag, sStyleDetectFromWord, sStyleInitMode, sStyleBaseUrl, sStyleUploadObject, sStyleAutoDir, sStyleBaseHref, sStyleContentPath, sStyleAutoRemote, sStyleShowBorder
Dim sStyleFileExt, sStyleFlashExt, sStyleImageExt, sStyleMediaExt, sStyleRemoteExt, sStyleFileSize, sStyleFlashSize, sStyleImageSize, sStyleMediaSize, sStyleRemoteSize
Dim sToolBarID, sToolBarName, sToolBarOrder, sToolBarButton

sPosition = sPosition & "��ʽ����"

If sAction = "STYLEPREVIEW" Then
	' ��ʽԤ��
	Call InitStyle()
	Call ShowStylePreview()
	Response.End
End If


Call Header()
Call Content()
Call Footer()


Sub Content()
	Select Case sAction
	Case "COPY"
		' ����һ��׼��ʽ
		Call InitStyle()
		Call DoCopy()
		Call ShowStyleList()
	Case "STYLEADD"
		' ������ʽ��
		Call ShowStyleForm("ADD")
	Case "STYLESET"
		' ��ʽ���ã��޸Ļ�鿴
		Call InitStyle()
		Call ShowStyleForm("SET")
	Case "STYLEADDSAVE"
		' ��ʽ��������
		Call CheckStyleForm()
		Call DoStyleAddSave()
	Case "STYLESETSAVE"
		' ��ʽ�����޸ı���
		Call CheckStyleForm()
		Call DoStyleSetSave()
		Call RemoveApplication()
	Case "STYLEDEL"
		' ��ʽɾ��
		Call InitStyle()
		Call DoStyleDel()
		Call ShowStyleList()
		Call RemoveApplication()
	Case "CODE"
		' ��ʾ���ô���
		Call InitStyle()
		Call ShowStyleCode()
	Case "TOOLBAR"
		' ��ʾ��������
		Call InitStyle()
		Call ShowToolBarList()
	Case "TOOLBARADD"
		' ����������
		Call InitStyle()
		Call DoToolBarAdd()
		Call ShowToolBarList()
		Call RemoveApplication()
	Case "TOOLBARMODI"
		' �޸Ĺ�����
		Call InitStyle()
		Call DoToolBarModi()
		Call ShowToolBarList()
		Call RemoveApplication()
	Case "TOOLBARDEL"
		' ɾ��������
		Call InitStyle()
		Call DoToolBarDel()
		Call ShowToolBarList()
		Call RemoveApplication()
	Case "BUTTONSET"
		' ��ť����
		Call InitStyle()
		Call InitToolBar()
		Call ShowButtonList()
	Case "BUTTONSAVE"
		' ��ť���ñ���
		Call InitStyle()
		Call InitToolBar()
		Call DoButtonSave()
		Call RemoveApplication()
	Case Else
		' ��ǰ������ʽ�б�
		Call ShowStyleList()
	End Select
End Sub


' ��ǰ������ʽ�б�
Sub ShowStyleList()
	Response.Write "<table border=0 cellpadding=0 cellspacing=0 width='100%' height=40><tr>" & _
		"<td class=highlight2><b>����Ϊ��ǰ������ʽ�б�</b></td>" & _
		"<td align=right><a href='?action=styleadd'>������ʽ</a></td></tr></table>"

	Response.Write "<table border=0 cellpadding=0 cellspacing=0 class=list1>" & _
		"<form action='?action=del' method=post name=myform>" & _
		"<tr align=center>" & _
			"<th width=80>��ʽ��</th>" & _
			"<th width=60>��ѿ��</th>" & _
			"<th width=60>��Ѹ߶�</th>" & _
			"<th width=200>˵��</th>" & _
			"<th width=180>����</th>" & _
		"</tr>"

	Dim sManage
	sSql = "select * from ewebeditor_style"
	oRs.Open sSql, oConn, 0, 1
	Do While Not oRs.Eof
		sManage = "<a href='?action=stylepreview&id=" & oRs("S_ID") & "' target='_blank'>Ԥ��</a>|<a href='?action=code&id=" & oRs("S_ID") & "'>����</a>|<a href='?action=styleset&id=" & oRs("S_ID") & "'>����</a>|<a href='?action=toolbar&id=" & oRs("S_ID") & "'>������</a>"
		If oRs("S_IsSys") = 1 Then
			sManage = sManage & "|<a href='?action=copy&id=" & oRs("S_ID") & "'>����</a>"
		Else
			sManage = sManage & "|<a href='?action=styledel&id=" & oRs("S_ID") & "'>ɾ��</a>"
		End If
		Response.Write "<tr align=center>" & _
			"<td>" & outHTML(oRs("S_Name")) & "</td>" & _
			"<td>" & oRs("S_Width") & "</td>" & _
			"<td>" & oRs("S_Height") & "</td>" & _
			"<td align=left>" & outHTML(oRs("S_Memo")) & "</td>" & _
			"<td>" & sManage & "</td>" & _
			"</tr>"
		oRs.MoveNext
	Loop
	oRs.Close
	
	Response.Write "</table>"

	Response.Write "<p class=highlight1><b>˵����</b>ϵͳ�Դ���ʽ����������ý����޸�ɾ����������鿴���ã�������ȡ�����һ��׼��ʽ��Ȼ��������ý����޸��Դﵽ�����½���ʽ��Ŀ�ġ�</p><br><br>"

End Sub

' ����һ��׼��ʽ
Sub DoCopy()
	' ֻ��ϵͳ��ʽ���п�������
	If nStyleIsSys <> 1 Then
		Exit Sub
	End If
	' �Զ�ȡ��Ч����ʽ������1......��...
	Dim i, b, sNewID, sNewName
	b = False
	i = 0
	Do While b = False
		i = i + 1
		sNewName = sStyleName & i
		sSql = "select s_id from ewebeditor_style where s_name='" & sNewName & "'"
		oRs.Open sSql, oConn, 0, 1
		If oRs.Eof And oRs.Bof Then
			b = True
		End If
		oRs.Close
	Loop
	' ����һ���׼��ʽ��ͬ�ļ�¼������ͬ
	sSql = "insert into ewebeditor_style(s_name,s_dir,s_css,s_uploaddir,s_width,s_height,s_memo,s_issys,s_fileext,s_flashext,s_imageext,s_mediaext, s_remoteext,s_filesize,s_flashsize,s_imagesize,s_mediasize,s_remotesize,s_stateflag,s_detectfromword,s_initmode,s_baseurl,s_uploadobject,s_basehref,s_contentpath) select '" & sNewName & "',s_dir,s_css,s_uploaddir,s_width,s_height,s_memo,0,s_fileext,s_flashext,s_imageext,s_mediaext,s_remoteext,s_filesize,s_flashsize,s_imagesize,s_mediasize,s_remotesize,s_stateflag,s_detectfromword,s_initmode,s_baseurl,s_uploadobject,s_basehref,s_contentpath from ewebeditor_style where s_id=" & sStyleID
	oConn.Execute sSql
	' ȡ����ʽ��ID
	sSql = "select s_id from ewebeditor_style where s_name='" & sNewName & "'"
	oRs.Open sSql, oConn, 0, 1
	sNewID = oRs(0)
	oRs.Close
	' ����������
	sSql = "insert into ewebeditor_toolbar(s_id,t_name,t_order,t_button) select " & sNewID & ",t_name,t_order,t_button from ewebeditor_toolbar where s_id=" & sStyleID
	oConn.Execute sSql
End Sub

' ��ʽ��
Sub ShowStyleForm(sFlag)
	Dim s_Title, s_Button, s_Action
	Dim s_FormStateFlag, s_FormDetectFromWord, s_FormInitMode, s_FormBaseUrl, s_FormUploadObject, s_FormAutoDir, s_FormAutoRemote, s_FormShowBorder
	
	If sFlag = "ADD" Then
		sStyleID = ""
		sStyleName = ""
		sStyleDir = "standard"
		sStyleCSS = "office"
		sStyleUploadDir = "UploadFile/"
		sStyleBaseHref = "http://Localhost/eWebEditor/"
		sStyleContentPath = "UploadFile/"
		sStyleWidth = "600"
		sStyleHeight = "400"
		sStyleMemo = ""
		nStyleIsSys = 0
		s_Title = "������ʽ"
		s_Action = "StyleAddSave"
		sStyleFileExt = "rar|zip|exe|doc|xls|chm|hlp"
		sStyleFlashExt = "swf"
		sStyleImageExt = "gif|jpg|jpeg|bmp"
		sStyleMediaExt = "rm|mp3|wav|mid|midi|ra|avi|mpg|mpeg|asf|asx|wma|mov"
		sStyleRemoteExt = "gif|jpg|bmp"
		sStyleFileSize = "500"
		sStyleFlashSize = "100"
		sStyleImageSize = "100"
		sStyleMediaSize = "100"
		sStyleRemoteSize = "100"
		sStyleStateFlag = "1"
		sStyleAutoRemote = "1"
		sStyleShowBorder = "0"
		sStyleUploadObject = "0"
		sStyleAutoDir = "0"
		sStyleDetectFromWord = "true"
		sStyleInitMode = "EDIT"
		sStyleBaseUrl = "0"
	Else
		sStyleName = inHTML(sStyleName)
		sStyleDir = inHTML(sStyleDir)
		sStyleCSS = inHTML(sStyleCSS)
		sStyleUploadDir = inHTML(sStyleUploadDir)
		sStyleBaseHref = inHTML(sStyleBaseHref)
		sStyleContentPath = inHTML(sStyleContentPath)
		sStyleMemo = inHTML(sStyleMemo)
		s_Title = "������ʽ"
		s_Action = "StyleSetSave"
	End If

	s_FormStateFlag = InitSelect("d_stateflag", Split("��ʾ|����ʾ", "|"), Split("1|0", "|"), sStyleStateFlag, "", "")
	s_FormAutoRemote = InitSelect("d_autoremote", Split("�Զ��ϴ�|���Զ��ϴ�", "|"), Split("1|0", "|"), sStyleAutoRemote, "", "")
	s_FormShowBorder = InitSelect("d_showborder", Split("Ĭ����ʾ|Ĭ�ϲ���ʾ", "|"), Split("1|0", "|"), sStyleShowBorder, "", "")
	s_FormUploadObject = InitSelect("d_uploadobject", Split("�޾�������ϴ���|ASPUpload�ϴ����|SA-FileUp�ϴ����|LyfUpload�ϴ����", "|"), Split("0|1|2|3", "|"), sStyleUploadObject, "", "")
	s_FormAutoDir = InitSelect("d_autodir", Split("��ʹ��|��Ŀ¼|����Ŀ¼|������Ŀ¼", "|"), Split("0|1|2|3", "|"), sStyleAutoDir, "", "")
	s_FormDetectFromWord = InitSelect("d_detectfromword", Split("�Զ��������ʾ|���Զ����", "|"), Split("true|false", "|"), sStyleDetectFromWord, "", "")
	s_FormInitMode = InitSelect("d_initmode", Split("����ģʽ|�༭ģʽ|�ı�ģʽ|Ԥ��ģʽ", "|"), Split("CODE|EDIT|TEXT|VIEW", "|"), sStyleInitMode, "", "")
	s_FormBaseUrl = InitSelect("d_baseurl", Split("���·��|���Ը�·��|����ȫ·��", "|"), Split("0|1|2", "|"), sStyleBaseUrl, "", "")

	If nStyleIsSys = 0 Then
		s_Button = "<tr><td align=center colspan=4><input type=image border=0 src='admin/submit.gif' align=absmiddle>&nbsp;<a href='javascript:document.myform.reset()'><img border=0 src='admin/reset.gif' align=absmiddle></a></td></tr>"
	Else
		s_Button = ""
	End If
	
	Response.Write "<table border=0 cellpadding=5 cellspacing=0 height=20 width='100%'><tr><td align=right><a href='javascript:history.back()'>����</a></td></tr></table>"

	Response.Write "<table border=0 cellpadding=0 cellspacing=0 align=center class=form1>" & _
			"<form action='?action=" & s_Action & "&id=" & sStyleID & "' method=post name=myform>" & _
			"<tr><th colspan=4>&nbsp;&nbsp;" & s_Title & "������Ƶ������ɿ�˵������*��Ϊ�����</th></tr>" & _
			"<tr><td width='15%' align=right>��ʽ���ƣ�</td><td width='35%'><input type=text class=input size=20 name=d_name title='���ô���ʽ�����֣���Ҫ��������ţ����50���ַ�����' value=""" & sStyleName & """> <span class=highlight2>*</span></td><td width='15%' align=right>��ʼģʽ��</td><td width='35%'>" & s_FormInitMode & " <span class=highlight2>*</span></td></tr>" & _
			"<tr><td width='15%' align=right>�ϴ������</td><td width='35%'>" & s_FormUploadObject & " <span class=highlight2>*</span></td><td width='15%' align=right>�Զ�Ŀ¼��</td><td width='35%'>" & s_FormAutoDir & " <span class=highlight2>*</span></td></tr>" & _
			"<tr><td width='15%' align=right>ͼƬĿ¼��</td><td width='35%'><input type=text class=input size=20 name=d_dir title='��Ŵ���ʽͼƬ�ļ���Ŀ¼����������ButtonImage�£����50���ַ�����' value=""" & sStyleDir & """> <span class=highlight2>*</span></td><td width='15%' align=right>��ʽĿ¼��</td><td width='35%'><input type=text class=input size=20 name=d_css title='��Ŵ���ʽcss�ļ���Ŀ¼����������CSS�£����50���ַ�����' value=""" & sStyleCSS & """> <span class=highlight2>*</span></td></tr>" & _
			"<tr><td width='15%' align=right>��ѿ�ȣ�</td><td width='35%'><input type=text class=input name=d_width size=20 title='�������Ч���Ŀ�ȣ�������' value='" & sStyleWidth & "'> <span class=highlight2>*</span></td><td width='15%' align=right>��Ѹ߶ȣ�</td><td width='35%'><input type=text class=input name=d_height size=20 title='�������Ч���ĸ߶ȣ�������' value='" & sStyleHeight & "'> <span class=highlight2>*</span></td></tr>" & _
			"<tr><td width='15%' align=right>״ ̬ ����</td><td width='35%'>" & s_FormStateFlag & " <span class=highlight2>*</span></td><td width='15%' align=right>Wordճ����</td><td width='35%'>" & s_FormDetectFromWord & " <span class=highlight2>*</span></td></tr>" & _
			"<tr><td width='15%' align=right>Զ���ļ���</td><td width='35%'>" & s_FormAutoRemote & " <span class=highlight2>*</span></td><td width='15%' align=right>ָ�����룺</td><td width='35%'>" & s_FormShowBorder & " <span class=highlight2>*</span></td></tr>" & _
			"<tr><td colspan=4><span class=highlight2>&nbsp;&nbsp;&nbsp;�ϴ��ļ���ϵͳ�ļ�·��������ã�ֻ����ʹ�����·��ģʽʱ����Ҫ������ʾ·��������·������</span></td></tr>" & _
			"<tr><td width='15%' align=right>·��ģʽ��</td><td width='35%'>" & s_FormBaseUrl & " <span class=highlight2>*</span> <a href='#baseurl'>˵��</a></td><td width='15%' align=right>�ϴ�·����</td><td width='35%'><input type=text class=input size=20 name=d_uploaddir title='�ϴ��ļ������·�������eWebEditor��Ŀ¼�ļ���·�������50���ַ�����' value=""" & sStyleUploadDir & """> <span class=highlight2>*</span></td></tr>" & _
			"<tr><td width='15%' align=right>��ʾ·����</td><td width='35%'><input type=text class=input size=20 name=d_basehref title='��ʾ����ҳ�����·����������&quot;/&quot;��ͷ�����50���ַ�����' value=""" & sStyleBaseHref & """></td><td width='15%' align=right>����·����</td><td width='35%'><input type=text class=input size=20 name=d_contentpath title='ʵ�ʱ����������е�·���������ʾ·����·����������&quot;/&quot;��ͷ�����50���ַ�����' value=""" & sStyleContentPath & """></td></tr>" & _
			"<tr><td colspan=4><span class=highlight2>&nbsp;&nbsp;&nbsp;�����ϴ��ļ����ͼ��ļ���С���ã��ļ���С��λΪKB��0��ʾû�����ƣ���</span></td></tr>" & _
			"<tr><td width='15%' align=right>ͼƬ���ͣ�</td><td width='35%'><input type=text class=input name=d_imageext size=20 title='����ͼƬ��ص��ϴ������250���ַ�����' value='" & sStyleImageExt & "'></td><td width='15%' align=right>ͼƬ���ƣ�</td><td width='35%'><input type=text class=input name=d_imagesize size=20 title='�����ͣ���λKB' value='" & sStyleImageSize & "'></td></tr>" & _
			"<tr><td width='15%' align=right>Flash���ͣ�</td><td width='35%'><input type=text class=input name=d_flashext size=20 title='���ڲ���Flash���������250���ַ�����' value='" & sStyleFlashExt & "'></td><td width='15%' align=right>Flash���ƣ�</td><td width='35%'><input type=text class=input name=d_flashsize size=20 title='�����ͣ���λKB' value='" & sStyleFlashSize & "'></td></tr>" & _
			"<tr><td width='15%' align=right>ý�����ͣ�</td><td width='35%'><input type=text class=input name=d_mediaext size=20 title='���ڲ���ý���ļ������250���ַ�����' value='" & sStyleMediaExt & "'></td><td width='15%' align=right>ý�����ƣ�</td><td width='35%'><input type=text class=input name=d_mediasize size=20 title='�����ͣ���λKB' value='" & sStyleMediaSize & "'></td></tr>" & _
			"<tr><td width='15%' align=right>�������ͣ�</td><td width='35%'><input type=text class=input name=d_fileext size=20 title='���ڲ��������ļ������250���ַ�����' value='" & sStyleFileExt & "'></td><td width='15%' align=right>�������ƣ�</td><td width='35%'><input type=text class=input name=d_filesize size=20 title='�����ͣ���λKB' value='" & sStyleFileSize & "'></td></tr>" & _
			"<tr><td width='15%' align=right>Զ�����ͣ�</td><td width='35%'><input type=text class=input name=d_remoteext size=20 title='�����Զ��ϴ�Զ���ļ������250���ַ�����' value='" & sStyleRemoteExt & "'></td><td width='15%' align=right>Զ�����ƣ�</td><td width='35%'><input type=text class=input name=d_remotesize size=20 title='�����ͣ���λKB' value='" & sStyleRemoteSize & "'></td></tr>" & _
			"<tr><td align=right>��ע˵����</td><td colspan=3><textarea class=textarea rows=7 cols=65 name=d_memo title='����ʽ��˵�����������ڵ���'>" & sStyleMemo & "</textarea></td></tr>" & s_Button & _
			"</form>" & _
			"</table>"

	Response.Write "<a name=baseurl></a><p><span class=highlight2><b>·��ģʽ����˵����</b></span><br>" & _
		"<b>���·����</b>ָ���е�����ϴ����Զ������ļ�·�����༭����""UploadFile/...""��""../UploadFile/...""��ʽ���֣���ʹ�ô�ģʽʱ����ʾ·��������·�������ʾ·��������""/""��ͷ�ͽ�β������·�������в�����""/""��ͷ��<br>" & _
		"<b>���Ը�·����</b>ָ���е�����ϴ����Զ������ļ�·�����༭����""/eWebEditor/UploadFile/...""������ʽ���֣���ʹ�ô�ģʽʱ����ʾ·��������·�������<br>" & _
		"<b>����ȫ·����</b>ָ���е�����ϴ����Զ������ļ�·�����༭����""http://xxx.xxx.xxx/eWebEditor/UploadFile/...""������ʽ���֣���ʹ�ô�ģʽʱ����ʾ·��������·�������</p><br><br>"

End Sub

' ��ʼ����ʽ������
Sub InitStyle()
	Dim b
	b = False
	sStyleID = Trim(Request("id"))
	If IsNumeric(sStyleID) = True Then
		sSql = "select * from ewebeditor_style where s_id=" & sStyleID
		oRs.Open sSql, oConn, 0, 1
		If Not oRs.Eof Then
			sStyleName = oRs("S_Name")
			sStyleDir = oRs("S_Dir")
			sStyleCSS = oRs("S_CSS")
			sStyleUploadDir = oRs("S_UploadDir")
			sStyleBaseHref = oRs("S_BaseHref")
			sStyleContentPath = oRs("S_ContentPath")
			sStyleWidth = CStr(oRs("S_Width"))
			sStyleHeight = CStr(oRs("S_Height"))
			sStyleMemo = oRs("S_Memo")
			nStyleIsSys = oRs("S_IsSys")
			sStyleFileExt = oRs("S_FileExt")
			sStyleFlashExt = oRs("S_FlashExt")
			sStyleImageExt = oRs("S_ImageExt")
			sStyleMediaExt = oRs("S_MediaExt")
			sStyleRemoteExt = oRs("S_RemoteExt")
			sStyleFileSize = oRs("S_FileSize")
			sStyleFlashSize = oRs("S_FlashSize")
			sStyleImageSize = oRs("S_ImageSize")
			sStyleMediaSize = oRs("S_MediaSize")
			sStyleRemoteSize = oRs("S_RemoteSize")
			sStyleStateFlag = CStr(oRs("S_StateFlag"))
			sStyleAutoRemote = CStr(oRs("S_AutoRemote"))
			sStyleShowBorder = CStr(oRs("S_ShowBorder"))
			sStyleUploadObject = CStr(oRs("S_UploadObject"))
			sStyleAutoDir = CStr(oRs("S_AutoDir"))
			sStyleDetectFromWord = oRs("S_DetectFromWord")
			sStyleInitMode = oRs("S_InitMode")
			sStyleBaseUrl = oRs("S_BaseUrl")
			b = True
		End If
		oRs.Close
	End If
	If b = False Then
		Go_Error "��Ч����ʽID�ţ���ͨ��ҳ���ϵ����ӽ��в�����"
	End If
End Sub

' �����ʽ���ύ����Ч��
Sub CheckStyleForm()
	sStyleName = Trim(Request("d_name"))
	sStyleDir = Trim(Request("d_dir"))
	sStyleCSS = Trim(Request("d_css"))
	sStyleUploadDir = Trim(Request("d_uploaddir"))
	sStyleBaseHref = Trim(Request("d_basehref"))
	sStyleContentPath = Trim(Request("d_contentpath"))
	sStyleWidth = Trim(Request("d_width"))
	sStyleHeight = Trim(Request("d_height"))
	sStyleMemo = Request("d_memo")
	sStyleImageExt = Request("d_imageext")
	sStyleFlashExt = Request("d_flashext")
	sStyleMediaExt = Request("d_mediaext")
	sStyleRemoteExt = Request("d_remoteext")
	sStyleFileExt = Request("d_fileext")
	sStyleImageSize = Request("d_imagesize")
	sStyleFlashSize = Request("d_flashsize")
	sStyleMediaSize = Request("d_mediasize")
	sStyleRemoteSize = Request("d_remotesize")
	sStyleFileSize = Request("d_filesize")
	sStyleStateFlag = Request("d_stateflag")
	sStyleAutoRemote = Request("d_autoremote")
	sStyleShowBorder = Request("d_showborder")
	sStyleUploadObject = Request("d_uploadobject")
	sStyleAutoDir = Request("d_autodir")
	sStyleDetectFromWord = Request("d_detectfromword")
	sStyleInitMode = Request("d_initmode")
	sStyleBaseUrl = Request("d_baseurl")

	sStyleUploadDir = Replace(sStyleUploadDir, "\", "/")
	sStyleBaseHref = Replace(sStyleBaseHref, "\", "/")
	sStyleContentPath = Replace(sStyleContentPath, "\", "/")
	If Right(sStyleUploadDir, 1) <> "/" Then sStyleUploadDir = sStyleUploadDir & "/"
	If Right(sStyleBaseHref, 1) <> "/" Then sStyleBaseHref = sStyleBaseHref & "/"
	If Right(sStyleContentPath, 1) <> "/" Then sStyleContentPath = sStyleContentPath & "/"

	If sStyleName = "" Or Get_TrueLen(sStyleName) > 50 Then
		Go_Error "��ʽ������Ϊ�գ��Ҳ�����50���ַ����ȣ�"
	End If
	If IsSafeStr(sStyleName) = False Then
		Go_Error "��ʽ��������������ַ���"
	End If
	If sStyleDir = "" Or Get_TrueLen(sStyleDir) > 50 Then
		Go_Error "��ťͼƬĿ¼������Ϊ�գ��Ҳ�����50���ַ����ȣ�"
	End If
	If IsSafeStr(sStyleDir) = False Then
		Go_Error "��ťͼƬĿ¼��������������ַ���"
	End If
	If sStyleCSS = "" Or Get_TrueLen(sStyleCSS) > 50 Then
		Go_Error "��ʽCSSĿ¼������Ϊ�գ��Ҳ�����50���ַ����ȣ�"
	End If
	If IsSafeStr(sStyleCSS) = False Then
		Go_Error "��ʽCSSĿ¼��������������ַ���"
	End If

	If sStyleUploadDir = "" Or Get_TrueLen(sStyleUploadDir) > 50 Then
		Go_Error "�ϴ�·������Ϊ�գ��Ҳ�����50���ַ����ȣ�"
	End If
	If IsSafeStr(sStyleUploadDir) = False Then
		Go_Error "�ϴ�·��������������ַ���"
	End If
	Select Case sStyleBaseUrl
	Case "0"
		If sStyleBaseHref = "" Or Get_TrueLen(sStyleBaseHref) > 50 Then
			Go_Error "��ʹ�����·��ģʽʱ����ʾ·������Ϊ�գ��Ҳ�����50���ַ����ȣ�"
		End If
		If IsSafeStr(sStyleBaseHref) = False Then
			Go_Error "��ʹ�����·��ģʽʱ����ʾ·��������������ַ���"
		End If
		If Left(sStyleBaseHref, 1) <> "/" Then
			Go_Error "��ʹ�����·��ģʽʱ����ʾ·��������&quot;/&quot;��ͷ��"
		End If

		If sStyleContentPath = "" Or Get_TrueLen(sStyleContentPath) > 50 Then
			Go_Error "��ʹ�����·��ģʽʱ������·������Ϊ�գ��Ҳ�����50���ַ����ȣ�"
		End If
		If IsSafeStr(sStyleContentPath) = False Then
			Go_Error "��ʹ�����·��ģʽʱ������·��������������ַ���"
		End If
		If Left(sStyleContentPath, 1) = "/" Then
			Go_Error "��ʹ�����·��ģʽʱ������·��������&quot;/&quot;��ͷ��"
		End If
	Case "1", "2"
		sStyleBaseHref = ""
		sStyleContentPath = ""
	End Select
	
	If IsNumeric(sStyleWidth) = False Then
		Go_Error "����д��Ч��������ÿ�ȣ�"
	End If
	If IsNumeric(sStyleHeight) = False Then
		Go_Error "����д��Ч��������ø߶ȣ�"
	End If

	If Get_TrueLen(sStyleImageExt) > 250 Then
		Go_Error "ͼƬ�ļ����Ͳ��ܴ���250���ַ����ȣ�"
	End If
	If Get_TrueLen(sStyleFlashExt) > 250 Then
		Go_Error "Flash�ļ����Ͳ��ܴ���250���ַ����ȣ�"
	End If
	If Get_TrueLen(sStyleMediaExt) > 250 Then
		Go_Error "ý���ļ����Ͳ��ܴ���250���ַ����ȣ�"
	End If
	If Get_TrueLen(sStyleFileExt) > 250 Then
		Go_Error "�����ļ����Ͳ��ܴ���250���ַ����ȣ�"
	End If
	If Get_TrueLen(sStyleRemoteExt) > 250 Then
		Go_Error "Զ���ļ����Ͳ��ܴ���250���ַ����ȣ�"
	End If

	If IsNumeric(sStyleImageSize) = False Then
		Go_Error "����д��Ч��ͼƬ���ƴ�С��"
	End If
	If IsNumeric(sStyleFlashSize) = False Then
		Go_Error "����д��Ч��Flash���ƴ�С��"
	End If
	If IsNumeric(sStyleMediaSize) = False Then
		Go_Error "����д��Ч��ý���ļ����ƴ�С��"
	End If
	If IsNumeric(sStyleFileSize) = False Then
		Go_Error "����д��Ч�������ļ����ƴ�С��"
	End If
	If IsNumeric(sStyleRemoteSize) = False Then
		Go_Error "����д��Ч��Զ���ļ����ƴ�С��"
	End If

End Sub

' ��ʽ��������
Sub DoStyleAddSave()
	sSql = "select * from ewebeditor_style where s_name='" & sStyleName & "'"
	oRs.Open sSql, oConn, 0, 1
	If Not oRs.Eof Then
		Go_Error "����ʽ���Ѿ����ڣ�������һ����ʽ����"
	End If
	oRs.Close

	sSql = "select * from ewebeditor_style where s_id=0"
	oRs.Open sSql, oConn, 1, 3
	oRs.AddNew
	oRs("S_Name") = sStyleName
	oRs("S_Dir") = sStyleDir
	oRs("S_CSS") = sStyleCSS
	oRs("S_UploadDir") = sStyleUploadDir
	oRs("S_BaseHref") = sStyleBaseHref
	oRs("S_ContentPath") = sStyleContentPath
	oRs("S_Width") = sStyleWidth
	oRs("S_Height") = sStyleHeight
	oRs("S_Memo") = sStyleMemo
	oRs("S_ImageExt") = sStyleImageExt
	oRs("S_FlashExt") = sStyleFlashExt
	oRs("S_MediaExt") = sStyleMediaExt
	oRs("S_FileExt") = sStyleFileExt
	oRs("S_RemoteExt") = sStyleRemoteExt
	oRs("S_ImageSize") = sStyleImageSize
	oRs("S_FlashSize") = sStyleFlashSize
	oRs("S_MediaSize") = sStyleMediaSize
	oRs("S_FileSize") = sStyleFileSize
	oRs("S_RemoteSize") = sStyleRemoteSize
	oRs("S_StateFlag") = sStyleStateFlag
	oRs("S_AutoRemote") = sStyleAutoRemote
	oRs("S_ShowBorder") = sStyleShowBorder
	oRs("S_UploadObject") = sStyleUploadObject
	oRs("S_AutoDir") = sStyleAutoDir
	oRs("S_DetectFromWord") = sStyleDetectFromWord
	oRs("S_InitMode") = sStyleInitMode
	oRs("S_BaseUrl") = sStyleBaseUrl
	oRs.Update
	sStyleID = oRs("S_ID")
	oRs.Close

	Response.Write "<br><table border=0 cellspacing=20 align=center>" & _
		"<tr valign=top><td><img src='admin/do_ok.gif' border=0></td><td><b><span class=highlight2>��ʽ���ӳɹ���</span></b><br><br><ul>������<br><br><li><a href='admin_default.asp'>���غ�̨������ҳ</a><li><a href='?'>������ʽ����</a><li><a href='?action=toolbar&id=" & sStyleID & "'>���ô���ʽ�µĹ�����</a></ul></td></tr>" & _
		"</table><br><br>"

End Sub


' ��ʽ�޸ı���
Sub DoStyleSetSave()
	sStyleID = Trim(Request("id"))
	If IsNumeric(sStyleID) = True Then
		' �Ƿ����ͬ��
		sSql = "select * from ewebeditor_style where s_name='" & sStyleName & "' and s_id<>" & sStyleID
		oRs.Open sSql, oConn, 0, 1
		If Not oRs.Eof Then
			Go_Error "����ʽ���Ѿ����ڣ�������һ����ʽ����"
		End If
		oRs.Close
		
		sSql = "select * from ewebeditor_style where s_id=" & sStyleID
		oRs.Open sSql, oConn, 1, 3
		If Not oRs.Eof Then
			If oRs("S_IsSys") = 1 Then
				Go_Error "ϵͳ��ʽ���������޸ģ�"
			End If
		Else
			Go_Error "��Ч����ʽID�ţ���ͨ��ҳ���ϵ����ӽ��в�����"
		End If
		oRs("S_Name") = sStyleName
		oRs("S_Dir") = sStyleDir
		oRs("S_CSS") = sStyleCSS
		oRs("S_UploadDir") = sStyleUploadDir
		oRs("S_BaseHref") = sStyleBaseHref
		oRs("S_ContentPath") = sStyleContentPath
		oRs("S_Width") = sStyleWidth
		oRs("S_Height") = sStyleHeight
		oRs("S_Memo") = sStyleMemo
		oRs("S_ImageExt") = sStyleImageExt
		oRs("S_FlashExt") = sStyleFlashExt
		oRs("S_MediaExt") = sStyleMediaExt
		oRs("S_FileExt") = sStyleFileExt
		oRs("S_RemoteExt") = sStyleRemoteExt
		oRs("S_ImageSize") = sStyleImageSize
		oRs("S_FlashSize") = sStyleFlashSize
		oRs("S_MediaSize") = sStyleMediaSize
		oRs("S_RemoteSize") = sStyleRemoteSize
		oRs("S_FileSize") = sStyleFileSize
		oRs("S_StateFlag") = sStyleStateFlag
		oRs("S_AutoRemote") = sStyleAutoRemote
		oRs("S_ShowBorder") = sStyleShowBorder
		oRs("S_UploadObject") = sStyleUploadObject
		oRs("S_AutoDir") = sStyleAutoDir
		oRs("S_DetectFromWord") = sStyleDetectFromWord
		oRs("S_InitMode") = sStyleInitMode
		oRs("S_BaseUrl") = sStyleBaseUrl
		oRs.Update
		oRs.Close
	Else
		Go_Error "��Ч����ʽID�ţ���ͨ��ҳ���ϵ����ӽ��в�����"
	End If

	Response.Write "<br><table border=0 cellspacing=20 align=center>" & _
		"<tr valign=top><td><img src='admin/do_ok.gif' border=0></td><td><b><span class=highlight2>��ʽ�޸ĳɹ���</span></b><br><br><ul>������<br><br><li><a href='admin_default.asp'>���غ�̨������ҳ</a><li><a href='?'>������ʽ����</a><li><a href='?action=toolbar&id=" & sStyleID & "'>���ô���ʽ�µĹ�����</a></ul></td></tr>" & _
		"</table><br><br>"

End Sub

' ��ʽɾ��
Sub DoStyleDel()
	If nStyleIsSys = 0 Then
		sSql = "delete from ewebeditor_style where s_id=" & sStyleID
		oConn.Execute sSql
		sSql = "delete from ewebeditor_toolbar where s_id=" & sStyleID
		oConn.Execute sSql
	End If
End Sub

' ��ʽԤ��
Sub ShowStylePreview()
	Response.Write "<html><head>" & _
		"<title>��ʽԤ��</title>" & _
		"<meta http-equiv='Content-Type' content='text/html; charset=gb2312'>" & _
		"</head><body>" & _
		"<input type=hidden name=content1  value=''>" & _
		"<iframe ID='eWebEditor1' src='ewebeditor.asp?id=content1&style=" & sStyleName & "' frameborder=0 scrolling=no width='" & sStyleWidth & "' HEIGHT='" & sStyleHeight & "'></iframe>" & _
		"</body></html>"
End Sub

' ��ʾ���ô���
Sub ShowStyleCode()
	Response.Write "<table border=0 cellpadding=5 cellspacing=0 height=20 width='100%'><tr><td align=right><a href='javascript:history.back()'>����</a></td></tr></table>"
	Response.Write "<p class=highlight2>��ʽ��<b>" & outHTML(sStyleName) & "</b>������ѵ��ô������£�����XXX��ʵ�ʹ����ı�������޸ģ���</p>"
	Response.Write "<textarea rows=5 cols=65 style='width:100%'><IFRAME ID=""eWebEditor1"" SRC=""ewebeditor.asp?id=XXX&style=" & sStyleName & """ FRAMEBORDER=""0"" SCROLLING=""no"" WIDTH=""" & sStyleWidth & """ HEIGHT=""" & sStyleHeight & """></IFRAME></textarea><br><br>"
End Sub

' ��ʾ���������б�
Sub ShowToolBarList()
	Response.Write "<table border=0 cellpadding=5 cellspacing=0 height=20 width='100%'><tr>" & _
		"<td class=highlight2><b>��ʽ��" & outHTML(sStyleName) & "���µĹ���������</b></td>" & _
		"<td align=right><a href='?'>������ʽ����</a></td></tr></table>"

	Dim s_AddForm, s_ModiForm

	' ���ӱ�
	If nStyleIsSys = 1 Then
		s_AddForm = ""
	Else
		' ȡ��ǰ��������
		Dim nMaxOrder
		sSql = "select max(T_order) from ewebeditor_toolbar where s_id=" & sStyleID
		oRs.Open sSql, oConn, 0, 1
		If IsNull(oRs(0)) Then
			nMaxOrder = 1
		Else
			nMaxOrder = oRs(0) + 1
		End If
		oRs.Close

		s_AddForm = "<hr width='95%' align=center size=1><table border=0 cellpadding=4 cellspacing=0 align=center>" & _
		"<form action='?id=" & sStyleID & "&action=toolbaradd' name='addform' method=post>" & _
		"<tr><td>����������<input type=text name=d_name size=20 class=input value='������" & nMaxOrder & "'> ����ţ�<input type=text name=d_order size=5 value='" & nMaxOrder & "' class=input> <input type=submit name=b1 value='����������'></td></tr>" & _
		"</form></table><hr width='95%' align=center size=1>"
	End If

	' �޸ı�
	Dim s_Manage, s_SubmitButton
	s_ModiForm = "<form action='?id=" & sStyleID & "&action=toolbarmodi' name=modiform method=post>" & _
		"<table border=0 cellpadding=0 cellspacing=0 align=center class=list1>" & _
		"<tr align=center><th>ID</th><th>��������</th><th>�����</th><th>����</th></tr>"
	sSql = "select * from ewebeditor_toolbar where s_id=" & sStyleID & " order by t_order asc"
	oRs.Open sSql, oConn, 0, 1
	Do While Not oRs.Eof
		s_Manage = "<a href='?id=" & sStyleID & "&action=buttonset&toolbarid=" & oRs("t_id") & "'>��ť����</a>"
		If nStyleIsSys <> 1 Then
			s_Manage = s_Manage & "|<a href='?id=" & sStyleID & "&action=toolbardel&delid=" & oRs("t_id") & "'>ɾ��</a>"
		End If
		s_ModiForm = s_ModiForm & "<tr align=center>" & _
			"<td>" & oRs("t_id") & "</td>" & _
			"<td><input type=text name='d_name" & oRs("t_id") & "' value=""" & inHTML(oRs("t_name")) & """ size=30 class=input></td>" & _
			"<td><input type=text name='d_order" & oRs("t_id") & "' value='" & oRs("t_order") & "' size=5 class=input></td>" & _
			"<td>" & s_Manage & "</td>" & _
			"</tr>"
		oRs.MoveNext
	Loop
	oRs.Close
	If nStyleIsSys = 1 Then
		s_SubmitButton = ""
	Else
		s_SubmitButton = "<p align=center><input type=submit name=b1 value=' �޸� '></p>"
	End If
	s_ModiForm = s_ModiForm & "</table>" & s_SubmitButton & "</form><br><br>"

	' �����
	Response.Write s_AddForm & s_ModiForm

End Sub

' ����������
Sub DoToolBarAdd()
	Dim s_Name, s_Order
	s_Name = Trim(Request("d_name"))
	s_Order = Trim(Request("d_order"))
	If s_Name = "" Or Get_TrueLen(s_Name) > 50 Then
		Go_Error "������������Ϊ�գ��ҳ��Ȳ��ܴ���50���ַ����ȣ�"
	End If
	If IsNumeric(s_Order) = False Then
		Go_Error "��Ч�Ĺ���������ţ�����ű���Ϊ���֣�"
	End If
	If nStyleIsSys = 1 Then
		Go_Error "ϵͳ�Դ���ʽ�µĹ�������������������"
	End If
	sSql = "select * from ewebeditor_toolbar where 1=0"
	oRs.Open sSql, oConn, 1, 3
	oRs.AddNew
	oRs("s_id") = sStyleID
	oRs("t_name") = s_Name
	oRs("t_order") = s_Order
	oRs("t_button") = ""
	oRs.Update
	oRs.Close
	Response.Write "<script language=javascript>alert(""��������" & outHTML(s_Name) & "�����Ӳ����ɹ���"");</script>"
End Sub

' �޸Ĺ�����
Sub DoToolBarModi()
	Dim s_Name, s_Order
	If nStyleIsSys = 1 Then
		Go_Error "ϵͳ�Դ���ʽ�µĹ��������������޸ģ�"
	End If

	sSql = "select * from ewebeditor_toolbar where s_id=" & sStyleID
	oRs.Open sSql, oConn, 1, 3
	Do While Not oRs.Eof
		s_Name = Trim(Request("d_name" & oRs("t_id")))
		s_Order = Trim(Request("d_order" & oRs("t_id")))
		If s_Name <> "" And IsNumeric(s_Order) = True Then
			If s_Name <> oRs("t_name") Or s_Order <> CStr(oRs("t_Order")) Then
				oRs("t_name") = s_Name
				oRs("t_order") = s_Order
				oRs.Update
			End If
		End If
		oRs.MoveNext
	Loop
	oRs.Close
	Response.Write "<script language=javascript>alert('�������޸Ĳ����ɹ���');</script>"

End Sub

' ɾ��������
Sub DoToolBarDel()
	Dim s_DelID
	s_DelID = Trim(Request("delid"))
	If nStyleIsSys = 1 Then
		Go_Error "ϵͳ�Դ���ʽ�µĹ�������������ɾ����"
	End If
	If IsNumeric(s_DelID) = True Then
		sSql = "delete from ewebeditor_toolbar where s_id=" & sStyleID & " and t_id=" & s_DelID
		oConn.Execute sSql
		Response.Write "<script language=javascript>alert('��������ID��" & s_DelID & "��ɾ�������ɹ���');</script>"
	End If
End Sub

' ��ʼ��������
Sub InitToolBar()
	Dim b
	b = False
	sToolBarID = Trim(Request("toolbarid"))
	If IsNumeric(sToolBarID) = True Then
		sSql = "select * from ewebeditor_toolbar where s_id=" & sStyleID & " and t_id=" & sToolBarID
		oRs.Open sSql, oConn, 0, 1
		If Not oRs.Eof Then
			sToolBarName = oRs("T_Name")
			sToolBarOrder = oRs("T_Order")
			sToolBarButton = oRs("T_Button")
			b = True
		End If
		oRs.Close
	End If
	If b = False Then
		Go_Error "��Ч�Ĺ�����ID�ţ���ͨ��ҳ���ϵ����ӽ��в�����"
	End If
End Sub

' ��ť����
Sub ShowButtonList()
	Dim i, n

	' ����
	Response.Write "<table border=0 cellpadding=5 cellspacing=0 height=30 width='100%'><tr>" & _
		"<td><b>��ǰ��ʽ��<span class=highlight2>" & outHTML(sStyleName) & "</span>&nbsp;&nbsp;��ǰ��������<span class=highlight2>" & outHTML(sToolBarName) & "</span></b></td>" & _
		"<td align=right><a href='?action=toolbar&id=" & sStyleID & "'>���ع���������</a> | <a href='?'>������ʽ����</a></td>" & _
		"</tr></table>"

	' ȡ���а�ť
	Dim aButtonCode(), aButtonTitle(), aButtonImage()
	sSql = "select * from ewebeditor_button where b_allowselect=1 order by b_order asc"
	oRs.Open sSql, oConn, 0, 1
	i = 0
	Do While Not oRs.Eof
		i = i + 1
		Redim Preserve aButtonCode(i)
		Redim Preserve aButtonTitle(i)
		Redim Preserve aButtonImage(i)
		aButtonCode(i) = oRs("B_Code")
		aButtonTitle(i) = oRs("B_Title")
		aButtonImage(i) = oRs("B_Image")
		oRs.MoveNext
	Loop
	oRs.Close


	' ȡ��ѡ�б�
	Dim s_Option1
	s_Option1 = ""
	For i = 1 To UBound(aButtonCode)
		s_Option1 = s_Option1 & "<option value='" & aButtonCode(i) & "'>" & aButtonTitle(i) & "</option>"
	Next

	' ȡ��ѡ�б�
	Dim aButton, s_Option2, s_Temp
	aButton = Split(sToolBarButton, "|")
	s_Option2 = ""
	For i = 0 To UBound(aButton)
		s_Temp = Code2Title(aButton(i), aButtonCode, aButtonTitle)
		If s_Temp <> "" Then
			s_Option2 = s_Option2 & "<option value='" & aButton(i) & "'>" & s_Temp & "</option>"
		End If
	Next


	'����Ϊ�ͻ��˲���ѡ��ű�
	'''''''''''''''''''''''''''''''''''
%>

<script language=javascript>
// ������ѡ
function Add() {
	var sel1=document.myform.d_b1;
	var sel2=document.myform.d_b2;
	if (sel1.selectedIndex<0) {
		alert("��ѡ��һ����ѡ��ť��");
		return;
	}
	sel2.options[sel2.length]=new Option(sel1.options[sel1.selectedIndex].innerHTML,sel1.options[sel1.selectedIndex].value);
}

// ����ѡ��ɾ��
function Del() {
	var sel=document.myform.d_b2;
	var nIndex = sel.selectedIndex;
	var nLen = sel.length;
	if (nLen<1) return;
	if (nIndex<0) {
		alert("��ѡ��һ����ѡ��ť��");
		return;
	}
	for (var i=nIndex;i<nLen-1;i++) {
		sel.options[i].value=sel.options[i+1].value;
		sel.options[i].innerHTML=sel.options[i+1].innerHTML;
	}
	sel.length=nLen-1;
}

// ���������ƶ�
function Up() {
	var sel=document.myform.d_b2;
	var nIndex = sel.selectedIndex;
	var nLen = sel.length;
	if ((nLen<1)||(nIndex==0)) return;
	if (nIndex<0) {
		alert("��ѡ��һ��Ҫ�ƶ�����ѡ��ť��");
		return;
	}
	var sValue=sel.options[nIndex].value;
	var sHTML=sel.options[nIndex].innerHTML;
	sel.options[nIndex].value=sel.options[nIndex-1].value;
	sel.options[nIndex].innerHTML=sel.options[nIndex-1].innerHTML;
	sel.options[nIndex-1].value=sValue;
	sel.options[nIndex-1].innerHTML=sHTML;
	sel.selectedIndex=nIndex-1;
}

// ���������ƶ�
function Down() {
	var sel=document.myform.d_b2;
	var nIndex = sel.selectedIndex;
	var nLen = sel.length;
	if ((nLen<1)||(nIndex==nLen-1)) return;
	if (nIndex<0) {
		alert("��ѡ��һ��Ҫ�ƶ�����ѡ��ť��");
		return;
	}
	var sValue=sel.options[nIndex].value;
	var sHTML=sel.options[nIndex].innerHTML;
	sel.options[nIndex].value=sel.options[nIndex+1].value;
	sel.options[nIndex].innerHTML=sel.options[nIndex+1].innerHTML;
	sel.options[nIndex+1].value=sValue;
	sel.options[nIndex+1].innerHTML=sHTML;
	sel.selectedIndex=nIndex+1;
}

// �ύ����
function checkform() {
	var sel=document.myform.d_b2;
	var nLen = sel.length;
	var str="";
	for (var i=0;i<nLen;i++) {
		if (i>0) str+="|";
		str+=sel.options[i].value;
	}
	document.myform.d_button.value=str;
	return true;
}

</script>

<%
	'''''''''''''''''''''''''''''''''''


	' ѡ�����ñ�
	Dim s_SubmitButton
	If nStyleIsSys = 1 Then
		s_SubmitButton = ""
	Else
		s_SubmitButton = "<input type=submit name=b value=' �������� '>"
	End If
	Response.Write "<table border=0 cellpadding=5 cellspacing=0 align=center>" & _
		"<form action='?action=buttonsave&id=" & sStyleID & "&toolbarid=" & sToolBarID & "' method=post name=myform onsubmit='return checkform()'>" & _
		"<tr align=center><td>��ѡ��ť</td><td></td><td>��ѡ��ť</td><td></td></tr>" & _
		"<tr align=center>" & _
			"<td><select name='d_b1' size=20 style='width:200px' ondblclick='Add()'>" & s_Option1 & "</select></td>" & _
			"<td><input type=button name=b1 value=' �� ' onclick='Add()'><br><br><input type=button name=b1 value=' �� ' onclick='Del()'></td>" & _
			"<td><select name='d_b2' size=20 style='width:200px' ondblclick='Del()'>" & s_Option2 & "</select></td>" & _
			"<td><input type=button name=b3 value='��' onclick='Up()'><br><br><br><input type=button name=b4 value='��' onclick='Down()'></td>" & _
		"</tr>" & _
		"<input type=hidden name='d_button' value=''>" & _
		"<tr><td colspan=4 align=right>" & s_SubmitButton & "</td></tr>" & _
		"</form></table>"


	' ��ʾͼƬ���ձ�
	Response.Write "<p class=highlight1><b>�����ǰ�ťͼƬ���ձ���������������ⰴť����ûͼ����</b></p>"
	Response.Write "<table border=1 cellpadding=3 cellspacing=0 width='100%'>"
	n = 0
	For i = 1 To UBound(aButtonCode)
		n = i Mod 4
		If n = 1 Then
			Response.Write "<tr>"
		End If
		Response.Write "<td>"
		If aButtonImage(i) <> "" Then
			Response.Write "<img border=0 align=absmiddle src='ButtonImage/standard/" & aButtonImage(i) & "'>"
		End If
		Response.Write aButtonTitle(i)
		Response.Write "</td>"
		If n = 0 Then
			Response.Write "</tr>"
		End If
	Next
	If n > 0 Then
		For i = 1 To 4 - n
			Response.Write "<td>&nbsp;</td>"
		Next
		Response.Write "</tr>"
	End if
	Response.Write "</table><br><br>"
End Sub

' �ɰ�ť����õ���ť����
Function Code2Title(s_Code, a_ButtonCode, a_ButtonTitle)
	Dim i
	Code2Title = ""
	For i = 1 To UBound(a_ButtonCode)
		If UCase(a_ButtonCode(i)) = UCase(s_Code) Then
			Code2Title = a_ButtonTitle(i)
			Exit Function
		End If
	Next
End Function

' ��ť���ñ���
Sub DoButtonSave()
	Dim s_Button
	s_Button = Trim(Request("d_button"))
	If nStyleIsSys = 1 Then
		Go_Error "ϵͳ�Դ���ʽ��������԰�ť�����޸ģ�"
	End If

	sSql = "select * from ewebeditor_toolbar where t_id=" & sToolBarID
	oRs.Open sSql, oConn, 1, 3
	If Not oRs.Eof Then
		oRs("T_Button") = s_Button
		oRs.Update
	End If
	oRs.Close

	Response.Write "<br><table border=0 cellspacing=20 align=center>" & _
		"<tr valign=top><td><img src='admin/do_ok.gif' border=0></td><td><b><span class=highlight2>��������ť���ñ���ɹ���</span></b><br><br><ul>������<br><br><li><a href='admin_default.asp'>���غ�̨������ҳ</a><li><a href='?'>������ʽ����</a><li><a href='?action=toolbar&id=" & sStyleID & "'>���ع���������</a><li><a href='?action=buttonset&id=" & sStyleID & "&toolbarid=" & sToolBarID & "'>�������ô˹������µİ�ť</a></ul></td></tr>" & _
		"</table><br><br>"

End Sub

Sub RemoveApplication()
	Dim aApplicationName, i
	aApplicationName = Application("eWebEditor_ApplicationName")
	If IsArray(aApplicationName) = True Then
		For i = 1 To UBound(aApplicationName)
			Application.Contents.Remove(aApplicationName(i))
		Next
		Application.Contents.Remove("eWebEditor_ApplicationName")
		Application.Contents.Remove("eWebEditor_ApplicationUrl")
	End If
End Sub

%>