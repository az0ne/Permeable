<!--#include file="Include/Startup.asp"-->
<!--#include file="Include/upfile_class.asp"-->
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
Server.ScriptTimeOut = 1800
' ��������
Dim sType, sStyleName
' ���ñ���
Dim sAllowExt, nAllowSize, sUploadDir, nUploadObject, nAutoDir, sBaseUrl, sContentPath
' �ӿڱ���
Dim sFileExt, sOriginalFileName, sSaveFileName, sPathFileName, nFileNum


Call DBConnBegin()		' ��ʼ�����ݿ�����
Call InitUpload()		' ��ʼ���ϴ�����
Call DBConnEnd()		' �Ͽ����ݿ�����


Dim sAction
sAction = UCase(Trim(Request.QueryString("action")))

Select Case sAction
Case "REMOTE"
	Call DoRemote()			' Զ���Զ���ȡ
Case "SAVE"
	Call ShowForm()			' ��ʾ�ϴ���
	Call DoSave()			' ���ļ�
Case Else
	Call ShowForm()			' ��ʾ�ϴ���
End Select



Sub ShowForm() 
%>
<HTML>
<HEAD>
<TITLE>�ļ��ϴ�</TITLE>
<meta http-equiv="Content-Type" content="text/html; charset=gb2312">
<style type="text/css">
body, a, table, div, span, td, th, input, select{font:9pt;font-family: "����", Verdana, Arial, Helvetica, sans-serif;}
body {padding:0px;margin:0px}
</style>

<script language="JavaScript" src="dialog/dialog.js"></script>

</head>
<body bgcolor=menu>

<form action="?action=save&type=<%=sType%>&style=<%=sStyleName%>" method=post name=myform enctype="multipart/form-data">
<input type=file name=uploadfile size=1 style="width:100%" onchange="originalfile.value=this.value">
<input type=hidden name=originalfile value="">
</form>

<script language=javascript>

var sAllowExt = "<%=sAllowExt%>";
// ����ϴ���
function CheckUploadForm() {
	if (!IsExt(document.myform.uploadfile.value,sAllowExt)){
		parent.UploadError("��ʾ��\n\n��ѡ��һ����Ч���ļ���\n֧�ֵĸ�ʽ�У�"+sAllowExt+"����");
		return false;
	}
	return true
}

// �ύ�¼��������
var oForm = document.myform ;
oForm.attachEvent("onsubmit", CheckUploadForm) ;
if (! oForm.submitUpload) oForm.submitUpload = new Array() ;
oForm.submitUpload[oForm.submitUpload.length] = CheckUploadForm ;
if (! oForm.originalSubmit) {
	oForm.originalSubmit = oForm.submit ;
	oForm.submit = function() {
		if (this.submitUpload) {
			for (var i = 0 ; i < this.submitUpload.length ; i++) {
				this.submitUpload[i]() ;
			}
		}
		this.originalSubmit() ;
	}
}

// �ϴ�����װ�����
try {
	parent.UploadLoaded();
}
catch(e){
}

</script>

</body>
</html>
<% 
End Sub 


' �������
Sub DoSave()

	' Ĭ��������ϴ���
	Call DoUpload_Class
	
	sPathFileName = sContentPath & sSaveFileName
	Call OutScript("parent.UploadSaved('" & sPathFileName & "');var obj=parent.dialogArguments.dialogArguments;if (!obj) obj=parent.dialogArguments;try{obj.addUploadFile('" & sOriginalFileName & "', '" & sSaveFileName & "', '" & sPathFileName & "');} catch(e){}")

End Sub

' �Զ���ȡԶ���ļ�
Sub DoRemote()
	Dim sContent, i
	For i = 1 To Request.Form("eWebEditor_UploadText").Count 
		sContent = sContent & Request.Form("eWebEditor_UploadText")(i) 
	Next
	If sAllowExt <> "" Then
		sContent = ReplaceRemoteUrl(sContent, sAllowExt)
	End If

	Response.Write "<HTML><HEAD><TITLE>Զ���ϴ�</TITLE><meta http-equiv='Content-Type' content='text/html; charset=gb2312'></head><body>" & _
		"<input type=hidden id=UploadText value=""" & inHTML(sContent) & """>" & _
		"</body></html>"

	Call OutScriptNoBack("parent.setHTML(UploadText.value);try{parent.addUploadFile('" & sOriginalFileName & "', '" & sSaveFileName & "', '" & sPathFileName & "');} catch(e){} parent.remoteUploadOK();")

End Sub

' �����ϴ���
Sub DoUpload_Class()
	On Error Resume Next
	Dim oUpload, oFile
	' �����ϴ�����
	Set oUpload = New upfile_class
	' ȡ���ϴ�����,��������ϴ�
	oUpload.GetData(nAllowSize*1024)

	If oUpload.Err > 0 Then
		Select Case oUpload.Err
		Case 1
			Call OutScript("parent.UploadError('��ѡ����Ч���ϴ��ļ���')")
		Case 2
			Call OutScript("parent.UploadError('���ϴ����ļ��ܴ�С������������ƣ�" & nAllowSize & "KB����')")
		End Select
		Response.End
	End If

	Set oFile = oUpload.File("uploadfile")
	sFileExt = LCase(oFile.FileExt)
	Call CheckValidExt(sFileExt)
	sOriginalFileName = oFile.FileName
	sSaveFileName = GetRndFileName(sFileExt)

	Dim str_Mappath
	str_Mappath = Server.Mappath(sUploadDir & sSaveFileName)
	sFileExt = LCase(Mid(str_Mappath, InstrRev(str_Mappath, ".") + 1))
	Call CheckValidExt(sFileExt)

	oFile.SaveToFile str_Mappath
	
	Set oFile = Nothing
	Set oUpload = Nothing
End Sub

' ȡ����ļ���
Function GetRndFileName(sExt)
	Dim sRnd
	Randomize
	sRnd = Int(900 * Rnd) + 100
	GetRndFileName = year(now) & month(now) & day(now) & hour(now) & minute(now) & second(now) & sRnd & "." & sExt
End Function

' ����ͻ��˽ű�
Sub OutScript(str)
	Response.Write "<script language=javascript>" & str & ";history.back()</script>"
End Sub
Sub OutScriptNoBack(str)
	Response.Write "<script language=javascript>" & str & "</script>"
End Sub


' �����չ������Ч��
Sub CheckValidExt(sExt)
	Dim b, i, aExt
	b = False
	aExt = Split(sAllowExt, "|")
	For i = 0 To UBound(aExt)
		If LCase(aExt(i)) = sExt Then
			b = True
			Exit For
		End If
	Next
	If b = False Then
		OutScript("parent.UploadError('��ʾ��\n\n��ѡ��һ����Ч���ļ���\n֧�ֵĸ�ʽ�У�"+sAllowExt+"����')")
		Response.End
	End If
End Sub


' ��ʼ���ϴ���������
Sub InitUpload()
	sType = UCase(Trim(Request.QueryString("type")))
	sStyleName = Get_SafeStr(Trim(Request.QueryString("style")))
	sSql = "select * from ewebeditor_style where s_name='" & sStyleName & "'"
	oRs.Open sSql, oConn, 0, 1
	If Not oRs.Eof Then
		sBaseUrl = oRs("S_BaseUrl")
		nUploadObject = oRs("S_UploadObject")
		nAutoDir = oRs("S_AutoDir")
		sUploadDir = oRs("S_UploadDir")
		Select Case sBaseUrl
		Case "0"
			sContentPath = oRs("S_ContentPath")
		Case "1"
			sContentPath = RelativePath2RootPath(sUploadDir)
		Case "2"
			sContentPath = RootPath2DomainPath(RelativePath2RootPath(sUploadDir))
		End Select

		Select Case sType
		Case "REMOTE"
			sAllowExt = oRs("S_RemoteExt")
			nAllowSize = oRs("S_RemoteSize")
		Case "FILE"
			sAllowExt = oRs("S_FileExt")
			nAllowSize = oRs("S_FileSize")
		Case "MEDIA"
			sAllowExt = oRs("S_MediaExt")
			nAllowSize = oRs("S_MediaSize")
		Case "FLASH"
			sAllowExt = oRs("S_FlashExt")
			nAllowSize = oRs("S_FlashSize")
		Case Else
			sAllowExt = oRs("S_ImageExt")
			nAllowSize = oRs("S_ImageSize")
		End Select
	Else
		OutScript("parent.UploadError('��Ч����ʽID�ţ���ͨ��ҳ���ϵ����ӽ��в�����')")
	End If
	oRs.Close
	sAllowExt = UCase(sAllowExt)
End Sub

' תΪ��·����ʽ
Function RelativePath2RootPath(url)
	Dim sTempUrl
	sTempUrl = url
	If Left(sTempUrl, 1) = "/" Then
		RelativePath2RootPath = sTempUrl
		Exit Function
	End If

	Dim sWebEditorPath
	sWebEditorPath = Request.ServerVariables("SCRIPT_NAME")
	sWebEditorPath = Left(sWebEditorPath, InstrRev(sWebEditorPath, "/") - 1)
	Do While Left(sTempUrl, 3) = "../"
		sTempUrl = Mid(sTempUrl, 4)
		sWebEditorPath = Left(sWebEditorPath, InstrRev(sWebEditorPath, "/") - 1)
	Loop
	RelativePath2RootPath = sWebEditorPath & "/" & sTempUrl
End Function

' ��·��תΪ������ȫ·����ʽ
Function RootPath2DomainPath(url)
	Dim sHost, sPort
	sHost = Split(Request.ServerVariables("SERVER_PROTOCOL"), "/")(0) & "://" & Request.ServerVariables("HTTP_HOST")
	sPort = Request.ServerVariables("SERVER_PORT")
	If sPort <> "80" Then
		sHost = sHost & ":" & sPort
	End If
	RootPath2DomainPath = sHost & url
End Function

'================================================
'��  �ã��滻�ַ����е�Զ���ļ�Ϊ�����ļ�������Զ���ļ�
'��  ����
'	sHTML		: Ҫ�滻���ַ���
'	sExt		: ִ���滻����չ��
'================================================
Function ReplaceRemoteUrl(sHTML, sExt)
	Dim s_Content
	s_Content = sHTML
	If IsObjInstalled("Microsoft.XMLHTTP") = False then
		ReplaceRemoteUrl = s_Content
		Exit Function
	End If
	
	Dim re, RemoteFile, RemoteFileurl, SaveFileName, SaveFileType
	Set re = new RegExp
	re.IgnoreCase  = True
	re.Global = True
	re.Pattern = "((http|https|ftp|rtsp|mms):(\/\/|\\\\){1}(([A-Za-z0-9_-])+[.]){1,}(net|com|cn|org|cc|tv|[0-9]{1,3})(\S*\/)((\S)+[.]{1}(" & sExt & ")))"

	Set RemoteFile = re.Execute(s_Content)
	Dim a_RemoteUrl(), n, i, bRepeat
	n = 0
	' ת�����ظ�����
	For Each RemoteFileurl in RemoteFile
		If n = 0 Then
			n = n + 1
			Redim a_RemoteUrl(n)
			a_RemoteUrl(n) = RemoteFileurl
		Else
			bRepeat = False
			For i = 1 To UBound(a_RemoteUrl)
				If UCase(RemoteFileurl) = UCase(a_RemoteUrl(i)) Then
					bRepeat = True
					Exit For
				End If
			Next
			If bRepeat = False Then
				n = n + 1
				Redim Preserve a_RemoteUrl(n)
				a_RemoteUrl(n) = RemoteFileurl
			End If
		End If		
	Next
	' ��ʼ�滻����
	nFileNum = 0
	For i = 1 To n
		SaveFileType = Mid(a_RemoteUrl(i), InstrRev(a_RemoteUrl(i), ".") + 1)
		SaveFileName = GetRndFileName(SaveFileType)
		If SaveRemoteFile(SaveFileName, a_RemoteUrl(i)) = True Then
			nFileNum = nFileNum + 1
			If nFileNum > 0 Then
				sOriginalFileName = sOriginalFileName & "|"
				sSaveFileName = sSaveFileName & "|"
				sPathFileName = sPathFileName & "|"
			End If
			sOriginalFileName = sOriginalFileName & Mid(a_RemoteUrl(i), InstrRev(a_RemoteUrl(i), "/") + 1)
			sSaveFileName = sSaveFileName & SaveFileName
			sPathFileName = sPathFileName & sContentPath & SaveFileName
			s_Content = Replace(s_Content, a_RemoteUrl(i), sContentPath & SaveFileName, 1, -1, 1)
		End If
	Next

	ReplaceRemoteUrl = s_Content
End Function

'================================================
'��  �ã�����Զ�̵��ļ�������
'��  ����s_LocalFileName ------ �����ļ���
'		 s_RemoteFileUrl ------ Զ���ļ�URL
'����ֵ��True  ----�ɹ�
'        False ----ʧ��
'================================================
Function SaveRemoteFile(s_LocalFileName, s_RemoteFileUrl)
	Dim Ads, Retrieval, GetRemoteData
	Dim bError
	bError = False
	SaveRemoteFile = False
	'On Error Resume Next
	Set Retrieval = Server.CreateObject("Microsoft.XMLHTTP")
	With Retrieval
		.Open "Get", s_RemoteFileUrl, False, "", ""
		.Send
		GetRemoteData = .ResponseBody
	End With
	Set Retrieval = Nothing

	If LenB(GetRemoteData) > nAllowSize*1024 Then
		bError = True
	Else
		Set Ads = Server.CreateObject("Adodb.Stream")
		With Ads
			.Type = 1
			.Open
			.Write GetRemoteData
			.SaveToFile Server.MapPath(sUploadDir & s_LocalFileName), 2
			.Cancel()
			.Close()
		End With
		Set Ads=nothing
	End If

	If Err.Number = 0 And bError = False Then
		SaveRemoteFile = True
	Else
		Err.Clear
	End If
End Function

'================================================
'��  �ã��������Ƿ��Ѿ���װ
'��  ����strClassString ----�����
'����ֵ��True  ----�Ѿ���װ
'        False ----û�а�װ
'================================================
Function IsObjInstalled(strClassString)
	On Error Resume Next
	IsObjInstalled = False
	Err = 0
	Dim xTestObj
	Set xTestObj = Server.CreateObject(strClassString)
	If 0 = Err Then IsObjInstalled = True
	Set xTestObj = Nothing
	Err = 0
End Function



%>