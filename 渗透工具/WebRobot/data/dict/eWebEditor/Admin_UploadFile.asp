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

Dim sStyleID, sUploadDir, sCurrDir, sDir

sPosition = sPosition & "�ϴ��ļ�����"

Call Header()
Call Content()
Call Footer()


Sub Content()
	If IsObjInstalled("Scripting.FileSystemObject") = False Then
		Response.Write "�˹���Ҫ�������֧���ļ�ϵͳ����FSO�������㵱ǰ�ķ�������֧�֣�"
		Exit Sub
	End If

	' ��ʼ���������
	Call InitParam()

	Select Case sAction
	Case "DELALL"			' ɾ�������ļ�
		Call DoDelAll()
	Case "DEL"				' ɾ��ָ���ļ�
		Call DoDel()
	Case "DELFOLDER"		' ɾ���ļ���
		Call DoDelFolder()
	End Select

	' ��ʾ�ļ��б�
	Call ShowList()
End Sub

' UploadFileĿ¼�µ������ļ��б�
Sub ShowList()

	Response.Write "<p align=right class=highlight2>" & _
		"<form action='?' method=post name=queryform>" & _
		"<b>ѡ����ʽĿ¼��</b><select name='id' size=1 onchange=""location.href='?id='+this.options[this.selectedIndex].value"">" & InitSelect(sStyleID, "select ('��ʽ��'+S_Name+'---Ŀ¼��'+S_UploadDir),S_ID from eWebEditor_Style order by S_ID asc", "ѡ��...") & "</select>" & _
		"</form></p>"
	
	If sCurrDir = "" Then Exit Sub

	Response.Write "<table border=0 cellpadding=0 cellspacing=0 class=list1>" & _
		"<form action='?id=" & sStyleID & "&dir=" & sDir & "&action=del' method=post name=myform>" & _
		"<tr align=center>" & _
			"<th width=50>����</th>" & _
			"<th width=140>�ļ���ַ</th>" & _
			"<th width=100>��С</th>" & _
			"<th width=130>������</th>" & _
			"<th width=130>�ϴ�����</th>" & _
			"<th width=30>ɾ��</th>" & _
		"</tr>"

	Dim sCurrPage, nCurrPage, nFileNum, nPageNum, nPageSize
	sCurrPage = Trim(Request("page"))
	nPageSize = 20
	If sCurrpage = "" Or Not IsNumeric(sCurrPage) Then
		nCurrPage = 1
	Else
		nCurrPage = CLng(sCurrPage)
	End If

	Dim oFSO, oUploadFolder, oUploadFiles, oUploadFile, sFileName

	Set oFSO = Server.CreateObject("Scripting.FileSystemObject")
	On Error Resume Next
	Set oUploadFolder = oFSO.GetFolder(Server.MapPath(sCurrDir))
	If Err.Number>0 Then
		Response.Write "</table>��Ч��Ŀ¼��"
		Exit Sub
	End If

	
	If sDir <> "" Then
		Response.Write "<tr align=center>" & _
			"<td><img border=0 src='sysimage/file/folderback.gif'></td>" & _
			"<td align=left colspan=5><a href=""?id=" & sStyleID & "&dir="
		If InstrRev(sDir, "/") > 1 Then
			Response.Write Left(sDir, InstrRev(sDir, "/") - 1)
		End If
		Response.Write """>������һ��Ŀ¼</a></td></tr>"
	End If

	Dim oSubFolder
	For Each oSubFolder In oUploadFolder.SubFolders
		Response.Write "<tr align=center>" & _
			"<td><img border=0 src='sysimage/file/folder.gif'></td>" & _
			"<td align=left colspan=4><a href=""?id=" & sStyleID & "&dir="
		If sDir <> "" Then
			Response.Write sDir & "/"
		End If
		Response.Write oSubFolder.Name & """>" & oSubFolder.Name & "</a></td>" & _
			"<td><a href='?id=" & sStyleID & "&dir=" & sDir & "&action=delfolder&foldername=" & oSubFolder.Name & "'>ɾ��</a></td></tr>"
	Next

	
	Set oUploadFiles = oUploadFolder.Files

	nFileNum = oUploadFiles.Count
	nPageNum = Int(nFileNum / nPageSize)
	If nFileNum Mod nPageSize > 0 Then
		nPageNum = nPageNum+1
	End If
	If nCurrPage > nPageNum Then
		nCurrPage = 1
	end If

	Dim i
	i = 0
	For Each oUploadFile In oUploadFiles
		i = i + 1
		If i > (nCurrPage - 1) * nPageSize And i <= nCurrPage * nPageSize Then
			sFileName = oUploadFile.Name
			Response.Write "<tr align=center>" & _
				"<td>" & FileName2Pic(sFileName) & "</td>" & _
				"<td align=left><a href=""" & sCurrDir & sFileName & """ target=_blank>" & sFileName & "</a></td>" & _
				"<td>" & oUploadFile.size & " B </td>" & _
				"<td>" & oUploadFile.datelastaccessed & "</td>" & _
				"<td>" & oUploadFile.datecreated & "</td>" & _
				"<td><input type=checkbox name=delfilename value=""" & sFileName & """></td></tr>"
		Elseif i > nCurrPage * nPageSize Then
			Exit For
		End If
	Next
	Set oUploadFolder = Nothing
	Set oUploadFiles = Nothing

	If nFileNum <= 0 Then
		Response.Write "<tr><td colspan=6>ָ��Ŀ¼�����ڻ�û���ļ���</td></tr>"
	End If
	Response.Write "</table>"

	If nFileNum > 0 Then
		' ��ҳ
		Response.Write "<table border=0 cellpadding=3 cellspacing=0 width='100%'><tr><td>"
		If nCurrPage > 1 Then
			Response.Write "<a href='?id=" & sStyleID & "&dir=" & sDir & "&page=1'>��ҳ</a>&nbsp;&nbsp;<a href='?id=" & sStyleID & "&dir=" & sDir & "&page="& nCurrPage - 1 & "'>��һҳ</a>&nbsp;&nbsp;"
		Else
			Response.Write "��ҳ&nbsp;&nbsp;��һҳ&nbsp;&nbsp;"
		End If
		If nCurrPage < i / nPageSize Then
			Response.Write "<a href='?id=" & sStyleID & "&dir=" & sDir & "&page=" & nCurrPage + 1 & "'>��һҳ</a>&nbsp;&nbsp;<a href='?id=" & sStyleID & "&dir=" & sDir & "&page=" & nPageNum & "'>βҳ</a>"
		Else
			Response.Write "��һҳ&nbsp;&nbsp;βҳ"
		End If
		Response.Write "&nbsp;&nbsp;&nbsp;&nbsp;��<b>" & nFileNum & "</b>��&nbsp;&nbsp;ҳ��:<b><span class=highlight2>" & nCurrPage & "</span>/" & nPageNum & "</b>&nbsp;&nbsp;<b>" & nPageSize & "</b>���ļ�/ҳ"
		Response.Write "</td></tr></table>"
	End If

	Response.Write "<p align=right><input type=submit name=b value=' ɾ��ѡ�����ļ� '> <input type=button name=b1 value=' ��������ļ� ' onclick=""javascript:if (confirm('��ȷ��Ҫ��������ļ���')) {location.href='admin_uploadfile.asp?id=" & sStyleID & "&dir=" & sDir & "&action=delall';}""></p></form>"

End Sub

' ɾ��ָ�����ļ�
Sub DoDel()
	On Error Resume Next
	Dim sFileName, oFSO, sMapFileName
	Set oFSO = Server.CreateObject("Scripting.FileSystemObject")
	For Each sFileName In Request.Form("delfilename")
		sMapFileName = Server.MapPath(sCurrDir & sFileName)
		If oFSO.FileExists(sMapFileName) Then
			oFSO.DeleteFile(sMapFileName)
		End If
	Next
	Set oFSO = Nothing
End Sub

' ɾ�����е��ļ�
Sub DoDelAll()
	On Error Resume Next
	Dim sFileName, oFSO, sMapFileName, oFolder, oFiles, oFile
	Set oFSO = Server.CreateObject("Scripting.FileSystemObject")
	Set oFolder = oFSO.GetFolder(Server.MapPath(sCurrDir))
	Set oFiles = oFolder.Files
	For Each oFile In oFiles
		sFileName = oFile.Name
		sMapFileName = Server.MapPath(sCurrDir & sFileName)
		If oFSO.FileExists(sMapFileName) Then
			oFSO.DeleteFile(sMapFileName)
		End If
	Next
	Set oFile = Nothing
	Set oFolder = Nothing
	Set oFSO = Nothing
End Sub

' ɾ���ļ���
Sub DoDelFolder()
	On Error Resume Next
	Dim sFolderName, oFSO, sMapFolderName
	Set oFSO = Server.CreateObject("Scripting.FileSystemObject")
	sFolderName = Trim(Request("foldername"))
	sMapFolderName = Server.Mappath(sCurrDir & sFolderName)
	If oFSO.FolderExists(sMapFolderName) = True Then
		oFSO.DeleteFolder(sMapFolderName)
	End If
	Set oFSO = Nothing
End Sub

' ���������Ƿ�֧��ĳһ����
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


' ���ļ���ȡͼ
Function FileName2Pic(sFileName)
	Dim sExt, sPicName
	sExt = UCase(Mid(sFileName, InstrRev(sFileName, ".")+1))
	Select Case sExt
	Case "TXT"
		sPicName = "txt.gif"
	Case "CHM", "HLP"
		sPicName = "hlp.gif"
	Case "DOC"
		sPicName = "doc.gif"
	Case "PDF"
		sPicName = "pdf.gif"
	Case "MDB"
		sPicName = "mdb.gif"
	Case "GIF"
		sPicName = "gif.gif"
	Case "JPG"
		sPicName = "jpg.gif"
	Case "BMP"
		sPicName = "bmp.gif"
	Case "PNG"
		sPicName = "pic.gif"
	Case "ASP", "JSP", "JS", "PHP", "PHP3", "ASPX"
		sPicName = "code.gif"
	Case "HTM", "HTML", "SHTML"
		sPicName = "htm.gif"
	Case "ZIP"
		sPicName = "zip.gif"
	Case "RAR"
		sPicName = "rar.gif"
	Case "EXE"
		sPicName = "exe.gif"
	Case "AVI"
		sPicName = "avi.gif"
	Case "MPG", "MPEG", "ASF"
		sPicName = "mp.gif"
	Case "RA", "RM"
		sPicName = "rm.gif"
	Case "MP3"
		sPicName = "mp3.gif"
	Case "MID", "MIDI"
		sPicName = "mid.gif"
	Case "WAV"
		sPicName = "audio.gif"
	Case "XLS"
		sPicName = "xls.gif"
	Case "PPT", "PPS"
		sPicName = "ppt.gif"
	Case "SWF"
		sPicName = "swf.gif"
	Case Else
		sPicName = "unknow.gif"
	End Select
	FileName2Pic = "<img border=0 src='sysimage/file/" & sPicName & "'>"
End Function

' ===============================================
' ��ʼ��������
'	v_InitValue	: ��ʼֵ
'	s_Sql		: �����ݿ���ȡֵʱ,select name,value from table
'	s_AllName	: ��ֵ������,��:"ȫ��","����","Ĭ��"
' ===============================================
Function InitSelect(v_InitValue, s_Sql, s_AllName)
	Dim i
	InitSelect = ""
	If s_AllName <> "" Then
		InitSelect = InitSelect & "<option value=''>" & s_AllName & "</option>"
	End If
	oRs.Open s_Sql, oConn, 0, 1
	Do While Not oRs.Eof
		InitSelect = InitSelect & "<option value=""" & inHTML(oRs(1)) & """"
		If CStr(oRs(1)) = CStr(v_InitValue) Then
			InitSelect = InitSelect & " selected"
		End If
		InitSelect = InitSelect & ">" & outHTML(oRs(0)) & "</option>"
		oRs.MoveNext
	Loop
	oRs.Close
End Function

' ===============================================
' ��ʼ���������
' ===============================================
Function InitParam()
	sStyleID = Trim(Request("id"))
	sUploadDir = ""
	If IsNumeric(sStyleID) = True Then
		sSql = "select S_UploadDir from eWebEditor_Style where S_ID=" & sStyleID
		oRs.Open sSql, oConn, 0, 1
		If Not oRs.Eof Then
			sUploadDir = oRs(0)
		End If
		oRs.Close
	End If
	If sUploadDir = "" Then
		sStyleID = ""
	Else
		sUploadDir = Replace(sUploadDir, "\", "/")
		If Right(sUploadDir, 1) <> "/" Then
			sUploadDir = sUploadDir & "/"
		End If
	End If
	sCurrDir = sUploadDir

	' ��ʽ�µ�Ŀ¼
	sDir = Trim(Request("dir"))
	If sDir <> "" Then
		If CheckValidDir(Server.Mappath(sUploadDir & sDir)) = True Then
			sCurrDir = sUploadDir & sDir & "/"
		Else
			sDir = ""
		End If
	End If
End Function

' ===============================================
' ���Ŀ¼����Ч��
' ===============================================
Function CheckValidDir(s_Dir)
	Dim oFSO
	Set oFSO = Server.CreateObject("Scripting.FileSystemObject")
	CheckValidDir = oFSO.FolderExists(s_Dir)
	Set oFSO = Nothing	
End Function
%>